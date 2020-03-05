#include "main.h"

string get_stdin() {
    std::string line;
    std::getline(std::cin, line);
    return line;
}

int handleError( int status, const char* func_name,
            const char* err_msg, const char* file_name,
            int line, void* userdata )
{
    //Do nothing -- will suppress console output
    return 0;   //Return value is not used
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

void check_stdin() {

    vector<string> lines;
    while (true) {
        auto start = chrono::steady_clock::now();
        try{
            auto line = get_stdin();
            // lines.push_back(line);
            auto args = json::parse(line);

            // to_node("status", "Got stdin line: " + args.dump());

            // First check if we need to set something
            if (args.count("SET") == 1) {
                string setting = args["SET"];
                set_command(setting);
            } else if (args.count("DETECTED_FACES")==1) {
                json_faces.push(args["DETECTED_FACES"]);
                to_node("status", json_faces.front().dump());
            } else if (args.count("DETECTED_GESTURES")==1) {
                json_gestures.push(args["DETECTED_GESTURES"]);
                // to_node("status", json_gestures.dump());
            } else if (args.count("DETECTED_OBJECTS")==1) {
                json_objects.push(args["DETECTED_OBJECTS"]);
                // to_node("status", json_objects.dump());
            } else if (args.count("RECOGNIZED_PERSONS")==1) {
                json_persons.push(args["RECOGNIZED_PERSONS"]);
                // to_node("status", json_persons.dump());
            }
        } catch (json::exception& e)
        {
            //  to_node("status","CPP Error: " + string(e.what()) + "; Line was " + line);
        }
        auto end = chrono::steady_clock::now();
        string str_perf = "Loop stdin took " + to_string(chrono::duration_cast<chrono::milliseconds>(end -start).count()) + " ms";
        // to_node("status",str_perf);
    }
}

void to_node(std::string topic, std::string payload) {
    json j;
    j[topic] = payload;
    cout << j.dump() << endl;
}


void parse_args(string arg) {
    try{ 
        to_node("status", "CPP Parsing arguments: " + arg);
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

        to_node("status", "Height: " + to_string(height_image) + " ...");

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
         to_node("status","Error: " + string(e.what()));
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

cv::Rect2i convert_back(float x, float y, float w, float h){
    return Rect2i(x * width_image, y * height_image, w * width_image, h * height_image);
} 

void draw_objects(Mat tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_objects || json_objects.empty())
        return; 

    json_object = json_objects.front();
    json_objects.pop();

    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_object.is_null()){
        for (auto& element : json_object) {
            Rect2i rect = convert_back(element["center"][0].get<float>(), element["center"][1].get<float>(), element["w_h"][0].get<float>(), element["w_h"][1].get<float>());
            rectangle(tmp_frame, rect, Scalar(55,255,55));
            putText(tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_faces(Mat tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_face || json_faces.empty())
        return; 

    json_face = json_faces.front();
    json_faces.pop();
    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_face.is_null()){
        for (auto& element : json_face) {
            Rect2i rect = convert_back(element["center"][0].get<float>(), element["center"][1].get<float>(), element["w_h"][0].get<float>(), element["w_h"][1].get<float>());
            rectangle(tmp_frame, rect, Scalar(55,255,55));
        
            putText(tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_elements(Mat tmp_frame, queue<json> elements_queue, Scalar color, bool flag_show) {
    if (!flag_show || elements_queue.empty())
        return;

    auto elements = elements_queue.front();
    elements_queue.pop();

    if (!elements.is_null()){
        for (auto& element : elements) {
            Rect2i rect = convert_back(element["center"][0].get<float>(), element["center"][1].get<float>(), element["w_h"][0].get<float>(), element["w_h"][1].get<float>());
            rectangle(tmp_frame, rect, color);
            // to_node("status", to_string(rect.x) + " " + to_string(rect.y));
            putText(tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,color,3);
        }
    } 

} 

void draw_gestures(Mat tmp_frame) {
    // Don't draw if we don't have to
    if (!show_captions_gestures || json_gestures.empty())
        return; 

    json_gesture = json_gestures.front();
    json_gestures.pop();

    // cuda::GpuMat c_tmp_frame = cuda::GpuMat(width_image, height_image, CV_8UC3);

    if (!json_gesture.is_null()){
        for (auto& element : json_gesture) {
            Rect2i rect = convert_back(element["center"][0].get<float>(), element["center"][1].get<float>(), element["w_h"][0].get<float>(), element["w_h"][1].get<float>());
            rectangle(tmp_frame, rect, Scalar(55,255,55));
            putText(tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        }
    } 
}

void draw_persons(Mat tmp_frame){
    if (!show_captions_persons || json_persons.empty())
        return;

    json_person = json_persons.front();
    json_persons.pop();    

    if (!json_person.is_null()){
        for (auto& element : json_person) {
            Rect2i rect = convert_back(element["center"][0].get<float>(), element["center"][1].get<float>(), element["w_h"][0].get<float>(), element["w_h"][1].get<float>());
            rectangle(tmp_frame, rect, Scalar(55,255,55));
            putText(tmp_frame, element["name"].get<std::string>() + "/ID:" + to_string(element["TrackID"].get<int>()),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
        
            if (element.count("face") > 0) {
                json face = element["face"];
                
                putText(tmp_frame, face["name"].get<std::string>(),Point(rect.x, rect.y),FONT_HERSHEY_COMPLEX,1,Scalar(55,255,55),3);
                putText(tmp_frame,"with id: " + face["id"].get<std::string>() , Point(rect.x, rect.y+50), FONT_HERSHEY_DUPLEX, 0.5, Scalar(255,255,255), 2);
				putText(tmp_frame,"and confidence: " + face["confidence"].get<std::string>() , Point(rect.x, rect.y+90), FONT_HERSHEY_DUPLEX, 0.5, Scalar(255,255,255), 2);
            
                if (face.count("center") > 0){
                    json center_face = face["center"];                     
                    Rect2i rect = convert_back(center_face["center"][0].get<float>(), center_face["center"][1].get<float>(), center_face["w_h"][0].get<float>(), center_face["w_h"][1].get<float>());
                    rectangle(tmp_frame, rect, Scalar(255,255,255));

                }
            }

            if (element.count("gestures") > 0){
                    json gestures = element["gestures"];
                    for (auto& gesture : gestures) {
                        Rect2i rect = convert_back(gesture["center"][0].get<float>(), gesture["center"][1].get<float>(), gesture["w_h"][0].get<float>(), gesture["w_h"][1].get<float>());
                        rectangle(tmp_frame, rect, Scalar(255,255,255));
                        putText(tmp_frame, gesture["name"].get<std::string>(),Point(rect.x, rect.y+60),FONT_HERSHEY_COMPLEX,1,Scalar(255,255,255),3);
                    }            
            }
        }
    }
} 






// GOGOGO
int main(int argc, char * argv[]) {
    redirectError(handleError);
    // Say hello
    to_node("status", "CPP Starting  ...");
    // Parse arguments
    if (argc > 1) {
        parse_args(argv[1]);
    } else {
        // DO something if args parse fails.
    }

    cv::namedWindow("Frame",WINDOW_NORMAL);


    load_images_gestures();
    to_node("status","Images loaded.");
    open_video_streams();
    to_node("status","Video streams loaded.");

    // std::thread()

    // Launch stdin checker
    // auto future = std::async(std::launch::async, get_stdin);
    thread t_stdin_reader(check_stdin);

    auto start = chrono::steady_clock::now();
    
    while (true) {
        // Check if stdin has new input
        // if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
        //     auto line = future.get();

        //     // Set a new line. Subtle race condition between the previous line
        //     // and this. Some lines could be missed. To aleviate, you need an
        //     // io-only thread. I'll give an example of that as well.
        //     future = std::async(std::launch::async, get_stdin);
        //     // to_node("status", "CPP Reading stdin ...");
        //     check_stdin(line);
        // }
        
        start = chrono::steady_clock::now();
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
            frame_current_camera = Mat(height_image, width_image, CV_8UC3);
        
        c_frame_camera.upload(frame_current_camera);
 
        // to_node("status", "Camera frame uploaded");
        // c_frame_to_draw = cuda::GpuMat(width_image, height_image, CV_8UC3);
        // c_frame_to_draw.setTo(Scalar::all(0));
        // to_node("status", "Frame prepared");
        Mat frame_to_draw(height_image, width_image, CV_8UC3);
        frame_to_draw.setTo(Scalar::all(0));

        to_node("status", "queue sizes: " + to_string(json_faces.size()) + " " +  to_string(json_objects.size()) + " " +  to_string(json_gestures.size())  );

        draw_elements(frame_to_draw, json_faces,Scalar(255,0,190), show_captions_face);
        // to_node("status", "Faces drawn");
        draw_elements(frame_to_draw, json_objects,Scalar(255,0,190), show_captions_objects);
        // to_node("status", "Objects drawn");
        draw_elements(frame_to_draw, json_gestures,Scalar(255,0,190), show_captions_gestures);
        // to_node("status", "Gestures drawn");
        // draw_persons(frame_to_draw);
        // to_node("status", "Persons drawn");

        c_frame_to_draw.upload(frame_to_draw);
        // to_node("status", "Elements drawn");
        cuda::GpuMat c_frame_mask(c_frame_to_draw.size(),CV_8U);
        cuda::cvtColor(c_frame_to_draw, c_frame_mask, COLOR_BGR2GRAY);

        cuda::GpuMat c_frame_to_show(c_frame_to_draw.size(),CV_8UC3);

        c_frame_to_show = c_frame_camera.clone();

        c_frame_to_draw.copyTo(c_frame_to_show, c_frame_mask);
        // to_node("status", "Mask copied");
        Mat frame_to_show, frame_mask;
        c_frame_to_show.download(frame_to_show);
        // c_frame_mask.download(frame_mask);
        // to_node("status", "Showing");

        auto end = chrono::steady_clock::now();
        string str_perf = "Loop took " + to_string(chrono::duration_cast<chrono::milliseconds>(end -start).count()) + " ms";
        // to_node("status",str_perf);
        // Mat mask(frame_to_show.size(), CV_8U);

        imshow("Frame",frame_to_show);
        waitKey(1);
    }
}