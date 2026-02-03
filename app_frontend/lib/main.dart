import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'screens/auth/login_screen.dart';

void main() {
  runApp(const SmartRetailApp());
}

class SmartRetailApp extends StatelessWidget {
  const SmartRetailApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Retail Surveillance',
      debugShowCheckedModeBanner: false,

      // We will define this theme in the next file
      theme: AppTheme.darkTheme,

      // Start at Login Screen
      home: const LoginScreen(),
    );
  }
}
