/****************************************************************************
** Meta object code from reading C++ file 'modbus_tcpserver.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.15.13)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../../../../amrROS2_ws/src/modbus_server/include/modbus_server/modbus_tcpserver.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'modbus_tcpserver.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.15.13. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_Modbus_TCP_Server_t {
    QByteArrayData data[12];
    char stringdata0[149];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_Modbus_TCP_Server_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_Modbus_TCP_Server_t qt_meta_stringdata_Modbus_TCP_Server = {
    {
QT_MOC_LITERAL(0, 0, 17), // "Modbus_TCP_Server"
QT_MOC_LITERAL(1, 18, 17), // "handleDeviceError"
QT_MOC_LITERAL(2, 36, 0), // ""
QT_MOC_LITERAL(3, 37, 20), // "QModbusDevice::Error"
QT_MOC_LITERAL(4, 58, 8), // "newError"
QT_MOC_LITERAL(5, 67, 11), // "regsWritten"
QT_MOC_LITERAL(6, 79, 29), // "QModbusDataUnit::RegisterType"
QT_MOC_LITERAL(7, 109, 5), // "table"
QT_MOC_LITERAL(8, 115, 7), // "address"
QT_MOC_LITERAL(9, 123, 4), // "size"
QT_MOC_LITERAL(10, 128, 14), // "onStateChanged"
QT_MOC_LITERAL(11, 143, 5) // "state"

    },
    "Modbus_TCP_Server\0handleDeviceError\0"
    "\0QModbusDevice::Error\0newError\0"
    "regsWritten\0QModbusDataUnit::RegisterType\0"
    "table\0address\0size\0onStateChanged\0"
    "state"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_Modbus_TCP_Server[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       3,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    1,   29,    2, 0x0a /* Public */,
       5,    3,   32,    2, 0x0a /* Public */,
      10,    1,   39,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void, 0x80000000 | 3,    4,
    QMetaType::Void, 0x80000000 | 6, QMetaType::Int, QMetaType::Int,    7,    8,    9,
    QMetaType::Void, QMetaType::Int,   11,

       0        // eod
};

void Modbus_TCP_Server::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<Modbus_TCP_Server *>(_o);
        (void)_t;
        switch (_id) {
        case 0: _t->handleDeviceError((*reinterpret_cast< QModbusDevice::Error(*)>(_a[1]))); break;
        case 1: _t->regsWritten((*reinterpret_cast< QModbusDataUnit::RegisterType(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< int(*)>(_a[3]))); break;
        case 2: _t->onStateChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 1:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< QModbusDataUnit::RegisterType >(); break;
            }
            break;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject Modbus_TCP_Server::staticMetaObject = { {
    QMetaObject::SuperData::link<QObject::staticMetaObject>(),
    qt_meta_stringdata_Modbus_TCP_Server.data,
    qt_meta_data_Modbus_TCP_Server,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *Modbus_TCP_Server::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *Modbus_TCP_Server::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_Modbus_TCP_Server.stringdata0))
        return static_cast<void*>(this);
    if (!strcmp(_clname, "rclcpp::Node"))
        return static_cast< rclcpp::Node*>(this);
    return QObject::qt_metacast(_clname);
}

int Modbus_TCP_Server::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
