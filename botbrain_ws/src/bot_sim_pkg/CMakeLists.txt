cmake_minimum_required(VERSION 3.8)
project(bot_sim_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY
    launch
    config
    worlds
  DESTINATION
    share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/unitree_sdk_shim_node.py
  scripts/kinematic_locomotion_node.py
  scripts/isaac_sim_runner.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_python_install_package(${PROJECT_NAME})

ament_package()
