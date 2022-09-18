import 'dart:async';
import 'package:control_pad/models/gestures.dart';
import 'package:control_pad/models/pad_button_item.dart';
import 'package:flutter/services.dart';
import 'package:flutter/material.dart';
import 'package:lite_rolling_switch/lite_rolling_switch.dart';
import 'package:control_pad/control_pad.dart';
import 'package:http/http.dart' as http;

String RFID = '';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations(
          [DeviceOrientation.landscapeRight, DeviceOrientation.landscapeLeft])
      .then((_) {
    runApp(const Myapp());
  });
}

class Myapp extends StatelessWidget {
  const Myapp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String mode = "manual";
  int button_index = 0;
  late String button_state = '';
  late var url;
  @override
  void initState() {
    super.initState();
    Timer.periodic(const Duration(seconds: 1), get_RFID);
  }

  void get_RFID(Timer time) {
    if (mode == "manual") {
      getData();
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    String padBUttonPressedCallback(int Index, Gestures gesture) {
      String index = "$Index";
      button_index = Index;
      if (mode == "manual") {
        if (Index == 0) {
          //right
          button_state = "right";
        } else if (Index == 1) {
          //back
          button_state = "backward";
        } else if (Index == 2) {
          //left
          button_state = "left";
        } else if (Index == 3) {
          //forward
          button_state = "forward";
        }

        if (gesture == Gestures.LONGPRESS || gesture == Gestures.TAPDOWN) {
          url = "http://192.168.4.1/$button_state";
          sendData(url);
        } else if (gesture == Gestures.LONGPRESSUP || gesture == Gestures.TAP) {
          url = "http://192.168.4.1/stop";
          sendData(url);
        }
      }

      return index;
    }

    void flash_control(String state) {
      url = "http://192.168.4.1/$state";
      sendData(url);
    }

    void mode_control(String car_mode) {
      url = "http://192.168.4.1/$car_mode";
      sendData(url);
    }

    return Scaffold(
      body: Column(children: [
        Row(
          children: [
            const Padding(
              padding: EdgeInsets.only(top: 50, left: 100),
              child: Text(" RFID  ",
                  style: TextStyle(
                      backgroundColor: Colors.blueGrey,
                      fontSize: 40,
                      color: Colors.white)),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 50, right: 70),
              child: Text("      $RFID     ",
                  style: const TextStyle(
                      backgroundColor: Colors.blueGrey,
                      fontSize: 40,
                      color: Colors.deepOrange)),
            ),
          ],
        ),
        Row(
          textDirection: TextDirection.rtl,
          children: [
            Padding(
                padding: const EdgeInsets.only(right: 75, left: 100),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Padding(
                        padding: const EdgeInsets.only(top: 50),
                        child: PadButtonsView(
                          buttonsPadding: 5.0,
                          backgroundPadButtonsColor: Colors.blueGrey,
                          buttons: [
                            PadButtonItem(
                                supportedGestures: [
                                  Gestures.LONGPRESS,
                                  Gestures.TAP,
                                  Gestures.TAPDOWN,
                                  Gestures.LONGPRESSUP
                                ],
                                backgroundColor: Colors.white,
                                index: 0,
                                buttonImage: Image.asset("assets/right.png"),
                                pressedColor: Colors.green),
                            PadButtonItem(
                                supportedGestures: [
                                  Gestures.LONGPRESS,
                                  Gestures.TAP,
                                  Gestures.TAPDOWN,
                                  Gestures.LONGPRESSUP
                                ],
                                backgroundColor: Colors.white,
                                index: 1,
                                buttonImage: Image.asset("assets/down.png"),
                                pressedColor: Colors.orange),
                            PadButtonItem(
                                supportedGestures: [
                                  Gestures.LONGPRESS,
                                  Gestures.TAP,
                                  Gestures.TAPDOWN,
                                  Gestures.LONGPRESSUP
                                ],
                                backgroundColor: Colors.white,
                                index: 2,
                                buttonImage: Image.asset("assets/left.png"),
                                pressedColor: Colors.red),
                            PadButtonItem(
                                supportedGestures: [
                                  Gestures.LONGPRESS,
                                  Gestures.TAP,
                                  Gestures.TAPDOWN,
                                  Gestures.LONGPRESSUP
                                ],
                                backgroundColor: Colors.white,
                                index: 3,
                                buttonImage: Image.asset("assets/up.png"),
                                pressedColor: Colors.blue),
                          ],
                          padButtonPressedCallback: padBUttonPressedCallback,
                        ))
                  ],
                )),
            Column(
              children: [
                Padding(
                  padding: const EdgeInsets.only(right: 50, top: 30),
                  child: SizedBox(
                    width: 270,
                    height: 70,
                    child: FittedBox(
                      fit: BoxFit.fill,
                      child: LiteRollingSwitch(
                        textSize: 12,
                        value: false,
                        textOn: 'AUTOMATIC',
                        textOff: 'MANUAL ',
                        colorOn: Colors.deepOrange,
                        colorOff: Colors.blueGrey,
                        iconOn: Icons.drive_eta,
                        iconOff: Icons.drive_eta,
                        onChanged: (bool state) {
                          if (state == false) {
                            mode = "manual";
                            mode_control(mode);
                          } else {
                            mode = "auto";
                            mode_control(mode);
                          }
                        },
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.only(right: 50, top: 40),
                  child: SizedBox(
                    width: 270,
                    height: 70,
                    child: FittedBox(
                      fit: BoxFit.fill,
                      child: LiteRollingSwitch(
                        textSize: 12,
                        value: false,
                        textOn: 'FLASH ON',
                        textOff: 'FLASH OFF',
                        colorOn: Colors.deepOrange,
                        colorOff: Colors.blueGrey,
                        iconOn: Icons.flash_on_sharp,
                        iconOff: Icons.flash_off_sharp,
                        onChanged: (bool state) {
                          if (state == false) {
                            flash_control("ledoff");
                          } else {
                            flash_control("ledon");
                          }
                        },
                      ),
                    ),
                  ),
                ),
              ],
            )
          ],
        ),
      ]),
    );
  }
}

Future sendData(var url) async {
  http.Response response = await http.get(Uri.parse(url));
}

Future getData() async {
  var url2 = "http://192.168.4.1/rfid";
  http.Response response = await http.get(Uri.parse(url2));
  RFID = response.body;
}
