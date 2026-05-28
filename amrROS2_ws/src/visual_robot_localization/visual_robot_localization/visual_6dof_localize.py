# Removed pycolmap dependency
from visual_robot_localization.place_recognition_querier import PlaceRecognitionQuerier
from visual_robot_localization.coordinate_transforms import colmap2ros_coord_transform
from visual_robot_localization.hloc_models import FeatureExtractor, FeatureMatcher
import hloc.extract_features
import hloc.match_features


import h5py
import torch
import numpy as np
import cv2
import scipy.spatial.transform
from collections import defaultdict
from pathlib import Path
from ast import literal_eval


class VisualPoseEstimator:

    def __init__(self,
                global_extractor_name,
                local_extractor_name,
                local_matcher_name,
                image_gallery_path,
                gallery_global_descriptor_path,
                gallery_local_descriptor_path,
                reference_sfm_path,
                ransac_thresh = 12):

        assert Path(image_gallery_path).exists, image_gallery_path
        assert Path(gallery_global_descriptor_path).exists, gallery_global_descriptor_path
        assert Path(gallery_local_descriptor_path).exists, gallery_local_descriptor_path
        assert Path(reference_sfm_path).exists, reference_sfm_path

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        extractor_confs = hloc.extract_features.confs.copy()
        matcher_confs = hloc.match_features.confs.copy()

        global_extractor = FeatureExtractor(extractor_confs[global_extractor_name])
        self.pr_querier = PlaceRecognitionQuerier(global_extractor, gallery_global_descriptor_path, image_gallery_path)

        # Visual 6DoF pose estimation init
        self.local_extractor = FeatureExtractor(extractor_confs[local_extractor_name])
        self.gallery_local_descriptor_file = h5py.File(gallery_local_descriptor_path, 'r')
        self.local_matcher = FeatureMatcher(matcher_confs[local_matcher_name])

        # Load the prebuilt colmap 3D pointcloud
        from hloc.utils.read_write_model import read_model
        self.cameras, self.images, self.points3D = read_model(reference_sfm_path, ext='.bin')
        self.query_camera = self.cameras[1]

        import pycolmap
        self.reconstruction = pycolmap.Reconstruction(reference_sfm_path)

        self.ransac_thresh = ransac_thresh
        self.db_name_to_id = {image.name: image.id for image in self.images.values()}

    def estimate_pose(self, query_img, topk, covisibility_clustering = True, exclude_best_match = False):

        # Retrieve topk similar gallery images
        ksmallest_filenames, _, ksmallest_odometries = self.pr_querier.match(query_img, topk)
        ksmallest_filenames = [filename.split('/')[-1] for filename in ksmallest_filenames]

        # For testing with images from same sequence remove the first match since its the image itself
        if exclude_best_match:
            ksmallest_filenames = ksmallest_filenames[1:]
            ksmallest_odometries = ksmallest_odometries[1:]

        # Get the sfm database id's of the images
        db_ids = []
        for n in ksmallest_filenames:
            if n not in self.db_name_to_id:
                print('Image {n} was retrieved but not in database')
                continue
            db_ids.append(self.db_name_to_id[n])

        # Get the local descriptors of the gallery images
        topk_gallery_images_local_descriptors = [self.gallery_local_descriptor_file[filename] for \
                                                filename in ksmallest_filenames]

        topk_gallery_images_local_descriptors = [{key: torch.tensor(value[:]).to(self.device) for \
                                                    key, value in descriptor.items()} for \
                                                    descriptor in topk_gallery_images_local_descriptors]

        topk_gallery_poses = [ literal_eval(odom)['pose']['pose'] for odom in ksmallest_odometries ]

        # Extract the local descriptors for the query image
        query_local_descriptors = self.local_extractor(query_img)

        gallery_matches = None
        # At least 2 feature descriptors needed to attempt feature matching
        if query_local_descriptors['descriptors'].size(dim=-1) > 1: 
            # The order of the descriptors matters! Query first.
            data = self.local_matcher.prepare_data(query_local_descriptors, topk_gallery_images_local_descriptors, query_img.shape[0:2])
            gallery_matches, _ = self.local_matcher(data)

        if covisibility_clustering:
            from hloc.localize_sfm import do_covisibility_clustering
            clusters = do_covisibility_clustering(db_ids, self.reconstruction)
        else:
            clusters = [db_ids]

        estimates = {} 
        estimates['pnp_estimates'] = []
        estimates['place_recognition'] = [{'tvec':np.array([pose['position']['x'],
                                                            pose['position']['y'],
                                                            pose['position']['z'] ]),

                                            'qvec':np.array([pose['orientation']['w'],
                                                             pose['orientation']['x'],
                                                             pose['orientation']['y'],
                                                             pose['orientation']['z'] ])
            } for pose in topk_gallery_poses]

        for cluster_ids in clusters:
            cluster_idxs = [ db_ids.index(id) for id in cluster_ids ]
            if gallery_matches is not None:
                cluster_matches = [gallery_matches[idx,:] for idx in cluster_idxs]
                # PnP to estimate the 6DoF location of the query image
                ret = self._pose_from_cluster_online(cluster_ids, cluster_matches, query_local_descriptors)
            else:
                # If local feature matching failed
                ret = {'success': False}

            ret['place_recognition_idx'] = cluster_idxs

            if ret['success']:
                ret['tvec'], ret['qvec'] = colmap2ros_coord_transform(ret['tvec'], ret['qvec'])

            estimates['pnp_estimates'].append(ret)

        return estimates

    def _pose_from_cluster_online(self, db_ids, query_matches, query_local_descriptors):

        # Magic to get the 3D points from the sfm database
        # that correspond to the matched 2D image features
        #
        # Adapted from hloc pose_from_cluster

        kp_idx_to_3D_to_db = defaultdict(lambda: defaultdict(list))
        kp_idx_to_3D = defaultdict(list)

        for i, db_id in enumerate(db_ids):
            matches = query_matches[i]

            image = self.images[db_id]
            points3D_ids = image.point3D_ids
            if len(np.where(points3D_ids != -1)[0]) == 0:
                print(f'No 3D points found for image {image.name}')
                continue
            
            valid = np.where(matches > -1)[0]
            valid = valid[points3D_ids[matches[valid]] != -1]

            for idx in valid:
                id_3D = points3D_ids[matches[idx]]
                kp_idx_to_3D_to_db[idx][id_3D].append(i)
                # avoid duplicate observations
                if id_3D not in kp_idx_to_3D[idx]:
                    kp_idx_to_3D[idx].append(id_3D)
        
        idxs = list(kp_idx_to_3D.keys())
        mkp_idxs = [i for i in idxs for _ in kp_idx_to_3D[i]]
        mkpq = query_local_descriptors['keypoints'][mkp_idxs]
        mkpq += 0.5  # COLMAP coordinates

        mp3d_ids = [j for i in idxs for j in kp_idx_to_3D[i]]
        mp3d = [self.points3D[j].xyz for j in mp3d_ids]
        mp3d = np.array(mp3d).reshape(-1, 3)

        if len(mp3d) < 4:
            return {'success': False, 'num_inliers': 0}

        # OpenCV PnP pose estimation
        mkpq_np = mkpq.cpu().numpy()
        camera = self.query_camera
        if camera.model == 'SIMPLE_PINHOLE':
            f, cx, cy = camera.params
            camera_matrix = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.zeros((4,1))
        elif camera.model == 'PINHOLE':
            fx, fy, cx, cy = camera.params
            camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.zeros((4,1))
        elif camera.model == 'SIMPLE_RADIAL':
            f, cx, cy, k = camera.params
            camera_matrix = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.array([k, 0, 0, 0], dtype=np.float64)
        else:
            # Fallback
            f, cx, cy = camera.params[0:3]
            camera_matrix = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float64)
            dist_coeffs = np.zeros((4,1))
            
        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            mp3d, mkpq_np, camera_matrix, dist_coeffs,
            reprojectionError=self.ransac_thresh, flags=cv2.SOLVEPNP_ITERATIVE)
        
        if success:
            r = scipy.spatial.transform.Rotation.from_rotvec(rvec.flatten())
            qvec = r.as_quat() # x, y, z, w
            qvec = np.array([qvec[3], qvec[0], qvec[1], qvec[2]]) # w, x, y, z
            return {'success': True, 'tvec': tvec.flatten(), 'qvec': qvec, 'num_inliers': len(inliers) if inliers is not None else 0}
        else:
            return {'success': False, 'num_inliers': 0}