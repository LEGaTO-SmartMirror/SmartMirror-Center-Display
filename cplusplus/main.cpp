#include "main.h"

string get_stdin() {
    std::string line;
    std::getline(std::cin, line);
    return line;
}

void set_command(string setting) {

    if (setting == "TOGGLE") {
            show_camera = !show_camera;
            show_style_transfer = false;
    } else if (setting == "DISTANCE") {
        show_camera_1m = !show_camera_1m;
    } else if (setting == "FACE") {
        show_captions_face = !show_captions_face;
    } else if (setting == "OBJECT") {
        show_captions_objects = !show_captions_objects;
    } else if (setting == "GESTURE") {
        show_captions_gestures = !show_captions_gestures;
    } else if (setting == "PERSON") {
        show_captions_persons = !show_captions_persons;
    }  else if (setting == "STYLE_TRANSFERE" && is_ai_art) {
        show_camera = false;
        show_camera_1m = false;
        show_captions_face = false;
        show_captions_objects = false;
        show_captions_gestures = false;
        show_captions_persons = false;
        show_style_transfer = !show_style_transfer;
    } else if (setting == "HIDEALL") {
        show_camera = false;
        show_camera_1m = false;
        show_captions_face = false;
        show_captions_objects = false;
        show_captions_gestures = false;
        show_captions_persons = false;
        show_style_transfer = false;
    } else if (setting == "SHOWALL") {
        show_camera = true;
        show_camera_1m = false;
        show_captions_face = true;
        show_captions_objects = true;
        show_captions_gestures = true;
        show_captions_persons = true;
        show_style_transfer = false;
    }
}

void check_stdin(string line) {
    try{
        auto args = json::parse(line);

        to_node("status", "Got stdin line: " + args.dump());

        // First check if we need to set something
        if (args.count("SET") == 1) {
            string setting = args["SET"];
            set_command(setting);
        } else if (args.count("DETECTED_FACES")==1) {
            json_faces = args["DETECTED_FACES"];
            to_node("status", json_faces.dump());
        } else if (args.count("DETECTED_GESTURES")==1) {
            json_gestures = args["DETECTED_GESTURES"];
            to_node("status", json_gestures.dump());
        } else if (args.count("DETECTED_OBJECTS")==1) {
            json_objects = args["DETECTED_OBJECTS"];
            to_node("status", json_objects.dump());
        } else if (args.count("RECOGNIZED_PERSONS")==1) {
            json_persons = args["RECOGNIZED_PERSONS"];
            to_node("status", json_persons.dump());
        }
    } catch (json::exception& e)
     {
        //  to_node("status","CPP Error: " + string(e.what()) + "; Line was " + line);
     }
}

void to_node(std::string topic, std::string payload) {
    json j;
    j[topic] = payload;
    cout << j.dump() << endl;
    // printf(j.dump().c_str()+'\n');
    // fflush(stdout);
    // printf("\n");
    // fflush(stdout);
}


void parse_args(string arg) {
    try{ 
        // to_node("status", "CPP Parsing arguments ...");
        auto args = json::parse(arg);
        // to_node("status", "CPP Arguments: " + args.dump());

        int height_present = args.count("image_height"); // 1 or 0
        int width_present = args.count("image_width"); // 1 or 0
        int ai_art_present = args.count("ai_art_mirror"); // 1 or 0
        int cap_video_present = args.count("gst_string_camera"); // 1 or 0
        int cap_video_1m_present = args.count("gst_string_camera_1m"); // 1 or 0
        int cap_video_style_present = args.count("gst_string_style"); // 1 or 0

        if (height_present)
            height_image = args["image_height"].get<int>();
        if (width_present)
            width_image = args["image_width"].get<int>();
        if (ai_art_present)
            is_ai_art = args["ai_art_mirror"].get<bool>();

        to_node("status", "Here1 ...");

        if (cap_video_present){ 
            gst_string_camera = args["gst_string_camera"].get<std::string>();
        } else {
            gst_string_camera = "shmsrc socket-path=/dev/shm/camera_image ! video/x-raw, format=BGR, height=" + to_string(height_image) + ", width=" + to_string(width_image) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true";
        } 

        to_node("status", "Here 2...");

        if (cap_video_1m_present){
            gst_string_camera_1m = args["gst_string_camera_1m"].get<std::string>();
        } else {
            gst_string_camera_1m = "shmsrc socket-path=/dev/shm/camera_1m ! video/x-raw, format=BGR, height=" + to_string(height_image) + ", width=" + to_string(width_image) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true";
        }

        to_node("status", "Here 3...");

        if (ai_art_present) {
            if (is_ai_art) {
                gst_string_style = args["gst_string_style"].get<std::string>();
            } else {
                gst_string_style = "shmsrc socket-path=/dev/shm/style_transfer ! video/x-raw, format=BGR, height=" + to_string(height_image) + ", width=" + to_string(width_image) + ", framerate=30/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true";
            }
        } 
    } catch (json::exception& e)
     {
        //  to_node("status","Error: " + string(e.what()));
     }

}

void open_video_streams() {
    while (!cap_video.isOpened()) {
        cap_video.open(gst_string_camera, CAP_GSTREAMER);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    while (!cap_video.isOpened()) {
        cap_video.open(gst_string_camera_1m, CAP_GSTREAMER);
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    if (is_ai_art) {
        while (!cap_video.isOpened()) {
            cap_video.open(gst_string_style, CAP_GSTREAMER);
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    } 
}

void load_images_gestures() {
    for (int i = 0; i < NUMBER_OF_GESTURES ; i++) {
        gesture_images[i] = imread(PATH_ICON_GESTURES + str_gestures[i] + ".jpg"); 
    } 
}

cv::Rect2i convert_back(int x, int y, int w, int h){
    return Rect2i(x * width_image, y * height_image, w * width_image, h * height_image);
} 

void draw_objects(cuda::GpuMat c_tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_objects)
        return; 

    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_objects.is_null()){
        for (auto& element : json_objects) {
            Rect2i rect = convert_back(element["center"][0].get<int>(), element["center"][1].get<int>(), element["w_h"][0].get<int>(), element["w_h"][1].get<int>());
            rectangle(c_tmp_frame, rect, Scalar(55,255,55));
            putText(c_tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_faces(cuda::GpuMat c_tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_face)
        return; 

    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_faces.is_null()){
        for (auto& element : json_faces) {
            Rect2i rect = convert_back(element["center"][0].get<int>(), element["center"][1].get<int>(), element["w_h"][0].get<int>(), element["w_h"][1].get<int>());
            rectangle(c_tmp_frame, rect, Scalar(55,255,55));
            putText(c_tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_elements(cuda::GpuMat c_tmp_frame, json elements, Scalar color, bool flag_show) {
    if (!flag_show)
        return;

    if (!elements.is_null()){
        for (auto& element : elements) {
            Rect2i rect = convert_back(element["center"][0].get<int>(), element["center"][1].get<int>(), element["w_h"][0].get<int>(), element["w_h"][1].get<int>());
            rectangle(c_tmp_frame, rect, color);
            putText(c_tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,color,3);
        }
    } 

} 

void draw_gestures(cuda::GpuMat c_tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_gestures)
        return; 

    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_gestures.is_null()){
        for (auto& element : json_gestures) {
            Rect2i rect = convert_back(element["center"][0].get<int>(), element["center"][1].get<int>(), element["w_h"][0].get<int>(), element["w_h"][1].get<int>());
            rectangle(c_tmp_frame, rect, Scalar(55,255,55));
            putText(c_tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_persons(cuda::GpuMat c_tmp_frame){
    if (!show_captions_persons)
        return;

    if (!json_persons.is_null()){
        for (auto& element : json_persons) {
            Rect2i rect = convert_back(element["center"][0].get<int>(), element["center"][1].get<int>(), element["w_h"][0].get<int>(), element["w_h"][1].get<int>());
            rectangle(c_tmp_frame, rect, Scalar(55,255,55));
            putText(c_tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        
            if (element.count("face") > 0) {
                json face = element["face"];
                
                putText(c_tmp_frame, face["name"].get<std::string>(),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
                putText(c_tmp_frame,"with id: " + face["id"].get<std::string>() , Point(rect.x, rect.y+50), FONT_HERSHEY_DUPLEX, 0.5, Scalar(255,255,255), 2);
				putText(c_tmp_frame,"and confidence: " + face["confidence"].get<std::string>() , Point(rect.x, rect.y+90), FONT_HERSHEY_DUPLEX, 0.5, Scalar(255,255,255), 2);
            
                if (face.count("center") > 0){
                    json center_face = face["center"];                     
                    Rect2i rect = convert_back(center_face["center"][0].get<int>(), center_face["center"][1].get<int>(), center_face["w_h"][0].get<int>(), center_face["w_h"][1].get<int>());
                    rectangle(c_tmp_frame, rect, Scalar(255,255,255));

                }
            }

            if (element.count("gestures") > 0){
                    json gestures = element["gestures"];
                    for (auto& gesture : gestures) {
                        Rect2i rect = convert_back(gesture["center"][0].get<int>(), gesture["center"][1].get<int>(), gesture["w_h"][0].get<int>(), gesture["w_h"][1].get<int>());
                        rectangle(c_tmp_frame, rect, Scalar(255,255,255));
                        putText(c_tmp_frame, gesture["name"].get<std::string>(),Point(rect.x, rect.y+60),FONT_HERSHEY_COMPLEX,1,Scalar(255,255,255),3);
                    }            
            }
        }
    }
} 



// GOGOGO
int main(int argc, char * argv[]) {
    // Say hello
    to_node("status", "CPP Starting  ...");
    // Parse arguments
    if (argc > 1) {
        parse_args(argv[1]);
    } else {
        // DO something if args parse fails.
    }


    load_images_gestures();

    open_video_streams();

    // Launch stdin checker
    auto future = std::async(std::launch::async, get_stdin);

    
    while (true) {
        // Check if stdin has new input
        if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
            auto line = future.get();

            // Set a new line. Subtle race condition between the previous line
            // and this. Some lines could be missed. To aleviate, you need an
            // io-only thread. I'll give an example of that as well.
            future = std::async(std::launch::async, get_stdin);
            to_node("status", "CPP Reading stdin ...");
            check_stdin(line);
        }

        // Read images from camera(s)
        if (show_camera){
            // if 1m camera is active, show that frame
            if (show_camera_1m)
                cap_video_1m >> frame_current_camera;
            else // if not, show normal RGB camera
                cap_video >> frame_current_camera;
        } else if (show_style_transfer) // if neither but style, show style
            cap_video_style >> frame_current_camera;
        else // Nothing selected, create empty frame to work on
            frame_current_camera = Mat(width_image, height_image, CV_8UC3);
        
        

        // to_node("status", "Here ...");
        c_frame_to_draw = cuda::GpuMat(width_image, height_image, CV_8UC3);
        c_frame_to_draw.setTo(Scalar::all(0));

    }
}