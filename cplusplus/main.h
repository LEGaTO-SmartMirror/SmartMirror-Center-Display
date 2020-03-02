#include <librealsense2/rs.hpp> // Include RealSense Cross Platform API
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <stdio.h>
#include <chrono>
#include <thread>
#include <signal.h>

#include <iostream>
#include <chrono>
#include <future>
#include <string>
#include <map>
#include <nlohmann/json.hpp>

// for convenience
using json = nlohmann::json;


using namespace std;
using namespace rs2;
using namespace cv;

int width_image;
int height_image;
bool is_ai_art;

const int NUMBER_OF_GESTURES = 12;

const string PATH_ICON_GESTURES = "icons/";

enum GESTURES {
    GESTURE_FLAT_RIGHT,
    GESTURE_FLAT_LEFT,
    GESTURE_OK_RIGHT,
    GESTURE_OK_LEFT,
    GESTURE_THUMPS_UP_RIGHT,
    GESTURE_THUMPS_UP_LEFT,
    GESTURE_THUMPS_DOWN_RIGHT,
    GESTURE_THUMPS_DOWN_LEFT,
    GESTURE_TWO_LEFT,
    GESTURE_TWO_RIGHT,
    GESTURE_ONE_LEFT,
    GESTURE_ONE_RIGHT
};

string str_gestures[NUMBER_OF_GESTURES] = {
    "flat_right",
    "flat_left",
    "okay_right",
    "okay_left",
    "thumps_up_right",
    "thumps_up_left",
    "thumps_down_right",
    "thumps_down_left",
    "two_left",
    "two_right",
    "one_left",
    "one_right"
};

VideoCapture cap_video, cap_video_1m, cap_video_style;
void open_video_streams();

cuda::GpuMat c_frame_to_draw;

cv::Mat gesture_images[NUMBER_OF_GESTURES]; 

Mat frame_current_camera;
cuda::GpuMat c_frame_camera, c_frame_camera_1m, c_frame_style;

std::map<char, cv::Mat> map_images_gestures;
void load_images_gestures();

cv::Rect2i convert_back(int x, int y, int w, int h);

string gst_string_camera, gst_string_camera_1m, gst_string_style;

bool show_captions_face;
bool show_captions_objects;
bool show_captions_gestures;
bool show_captions_persons;
bool show_camera;
bool show_camera_1m;
bool show_style_transfer;

json json_faces;
json json_gestures;
json json_objects;
json json_persons;

void draw_faces(cuda::GpuMat c_tmp_frame);
void draw_objects(cuda::GpuMat c_tmp_frame);
void draw_gestures(cuda::GpuMat c_tmp_frame);
void draw_persons(cuda::GpuMat c_tmp_frame);

void draw_elements(cuda::GpuMat c_tmp_frame, json elements, Scalar color, bool flag_show);

void parse_args(string args);
std::string check_stdin();
void to_node(std::string topic, std::string payload);
int main(int argc, char * argv[]);
