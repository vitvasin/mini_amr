/*
 * =====================================================================================
 *
 *       Filename:  main.cpp
 *
 *    Description:
 *
 *        Version:  1.0
 *        Created:  06/23/2023 01:16:27 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  YOUR NAME (),
 *   Organization:
 *
 * =====================================================================================
 */
#include <rclcpp/rclcpp.hpp>
// #include <libros2qt/qt_executor.h>
#include <QCoreApplication>
#include "modbus_tcpserver.h"
#include <signal.h>
#include <unistd.h>
#include <initializer_list>

void catchUnixSignals(std::initializer_list<int> quitSignals)
{
    auto handler = [](int sig) -> void
    {
        printf("Quit the Application by Signal(%d).\n", sig);
        QCoreApplication::quit();
    };

    sigset_t blocking_mask;
    sigemptyset(&blocking_mask);
    for (auto sig : quitSignals)
        sigaddset(&blocking_mask, sig);

    struct sigaction sa;
    sa.sa_handler = handler;
    sa.sa_mask = blocking_mask;
    sa.sa_flags = 0;

    for (auto sig : quitSignals)
        sigaction(sig, &sa, nullptr);
}

int main(int argc, char *argv[])
{
    QCoreApplication myApp(argc, argv);
    rclcpp::init(argc, argv);

    catchUnixSignals({SIGQUIT, SIGINT, SIGTERM, SIGHUP});

    auto modbus_server = std::make_shared<Modbus_TCP_Server>(&myApp);

    auto executor = std::make_shared<rclcpp::executors::MultiThreadedExecutor>();
    executor->add_node(modbus_server);

    std::thread ros_thread([&executor]()
                           { executor->spin(); });

    int result = myApp.exec();

    executor->cancel();
    if (ros_thread.joinable())
    {
        ros_thread.join();
    }

    rclcpp::shutdown();
    return result;

    // executor.start();
    // auto result = myApp.exec();
    // rclcpp::shutdown();
    // return result;

    //-------------------------------------------

    // QCoreApplication myApp(argc, argv);
    // rclcpp::init(argc, argv);

    // catchUnixSignals({SIGQUIT, SIGINT, SIGTERM, SIGHUP});

    // auto modbus_server = std::make_shared<Modbus_TCP_Server>(&myApp);

    // QtExecutor executor;
    // executor.add_node(modbus_server);

    // executor.start();
    // auto result = myApp.exec();
    // rclcpp::shutdown();
    // return result;
}
