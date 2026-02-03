import 'package:flutter/material.dart';

class AlertsScreen extends StatelessWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Security Alerts"),
      ),
      body: ListView.builder(
        itemCount: 5, // Mock data count
        itemBuilder: (context, index) {
          return Card(
            margin: const EdgeInsets.all(8),
            child: ListTile(
              leading: const Icon(Icons.warning, color: Colors.orange),
              title: Text("Suspicious Activity #${index + 1}"),
              subtitle: Text(
                  "Camera 1 • ${DateTime.now().toString().substring(0, 16)}"),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // Future: Show snapshot image
              },
            ),
          );
        },
      ),
    );
  }
}
