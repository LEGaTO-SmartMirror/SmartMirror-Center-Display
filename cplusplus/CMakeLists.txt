cmake_minimum_required(VERSION 2.8.3)


ADD_DEFINITIONS(
    -std=c++17 # Or -std=c++0x
    # Other flags
)



project(center_display)

find_package(nlohmann_json 3.2.0 REQUIRED)
find_package(OpenCV 4.1 REQUIRED)

find_package(PkgConfig)

include_directories(
  ${OpenCV_INCLUDES}
)


add_executable(center_display main.cpp)
target_link_libraries(center_display
  ${OpenCV_LIBRARIES}
  pthread
)

