// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from custom_interface:msg/Initdock.idl
// generated code does not contain a copyright notice

#include "custom_interface/msg/detail/initdock__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_custom_interface
const rosidl_type_hash_t *
custom_interface__msg__Initdock__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xf7, 0x5e, 0x07, 0x7f, 0xa6, 0x8e, 0x76, 0x7c,
      0x7a, 0x14, 0xa7, 0x07, 0x88, 0xa0, 0x55, 0x35,
      0x03, 0x81, 0xc2, 0x83, 0xdc, 0xeb, 0x16, 0xd6,
      0xbe, 0x38, 0x43, 0x54, 0x2d, 0x3e, 0x1c, 0x26,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char custom_interface__msg__Initdock__TYPE_NAME[] = "custom_interface/msg/Initdock";

// Define type names, field names, and default values
static char custom_interface__msg__Initdock__FIELD_NAME__x[] = "x";
static char custom_interface__msg__Initdock__FIELD_NAME__y[] = "y";
static char custom_interface__msg__Initdock__FIELD_NAME__z[] = "z";
static char custom_interface__msg__Initdock__FIELD_NAME__w[] = "w";

static rosidl_runtime_c__type_description__Field custom_interface__msg__Initdock__FIELDS[] = {
  {
    {custom_interface__msg__Initdock__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {custom_interface__msg__Initdock__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {custom_interface__msg__Initdock__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {custom_interface__msg__Initdock__FIELD_NAME__w, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
custom_interface__msg__Initdock__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {custom_interface__msg__Initdock__TYPE_NAME, 29, 29},
      {custom_interface__msg__Initdock__FIELDS, 4, 4},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float64 x\n"
  "float64 y\n"
  "float64 z\n"
  "float64 w";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
custom_interface__msg__Initdock__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {custom_interface__msg__Initdock__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 39, 39},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
custom_interface__msg__Initdock__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *custom_interface__msg__Initdock__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
