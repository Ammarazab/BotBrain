cmake_minimum_required(VERSION 3.8)
project(b2_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY
    config
    urdf
    meshes
    xacro
    launch
    maps
  DESTINATION
    share/${PROJECT_NAME}/
)

# Python nodes and modules
install(PROGRAMS
  scripts/b2_read.py
  scripts/b2_write.py
  scripts/b2_controller_commands.py
  scripts/b2_video_stream.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_python_install_package(${PROJECT_NAME})

ament_package()
