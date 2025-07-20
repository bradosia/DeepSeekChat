cmake_minimum_required(VERSION 3.16)
project(DeepSeekChat LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Set the source directory
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Find Qt6
find_package(Qt6 REQUIRED COMPONENTS Widgets)

# Add source files
add_executable(DeepSeekChat
    ${SRC_DIR}/main.cpp
    ${SRC_DIR}/MainWindow.cpp
    ${SRC_DIR}/MainWindow.h
    ${SRC_DIR}/MainWindow.ui
)

# Link against Qt6 Widgets
target_link_libraries(DeepSeekChat Qt6::Widgets)

# Set the working directory for runtime
set_target_properties(DeepSeekChat PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)
