import 'package:flutter/material.dart';
import 'package:flutter_mjpeg/flutter_mjpeg.dart';
import '../../core/constants.dart';

class LiveFeedScreen extends StatelessWidget {
  const LiveFeedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Live Surveillance"),
        backgroundColor: Colors.redAccent[700],
      ),
      body: Column(
        children: [
          // 1. Video Player Area
          Expanded(
            flex: 3,
            child: Center(
              child: Mjpeg(
                isLive: true,
                stream: AppConstants.videoStream, // Connects to Flask
                error: (context, error, stack) {
                  return const Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error, color: Colors.red, size: 50),
                      SizedBox(height: 10),
                      Text(
                        "Camera Offline\nCheck Server at ${AppConstants.baseUrl}",
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.white),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),

          // 2. Control Panel
          Expanded(
            flex: 2,
            child: Container(
              color: const Color(0xFF1E1E1E),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Active Camera: CAM-01",
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "Status: Monitoring for suspicious activity...",
                    style: TextStyle(color: Colors.grey),
                  ),
                  const Spacer(),
                  // Panic Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        padding: const EdgeInsets.all(15),
                      ),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                                content: Text("Manual Alarm Triggered!")));
                      },
                      icon: const Icon(Icons.warning_amber_rounded),
                      label: const Text("TRIGGER ALARM"),
                    ),
                  )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
