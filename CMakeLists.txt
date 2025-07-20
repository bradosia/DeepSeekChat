cmake_minimum_required(VERSION 3.16)
project(DeepSeekChat LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Find and link Qt6 Widgets
find_package(Qt6 REQUIRED COMPONENTS Widgets)

add_executable(DeepSeekChat
    main.cpp
    MainWindow.cpp
    MainWindow.h
    MainWindow.ui
)

target_link_libraries(DeepSeekChat Qt6::Widgets)