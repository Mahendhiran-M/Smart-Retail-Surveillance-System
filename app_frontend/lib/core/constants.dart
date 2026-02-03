class AppConstants {
  // ---------------------------------------------------
  // ⚠️ CRITICAL SETUP STEP:
  // Replace this IP with your Laptop's IPv4 Address.
  // Run 'ipconfig' in terminal to find it.
  // Example: "192.168.1.10"
  // ---------------------------------------------------
  static const String baseUrl = "http://192.168.29.64:5000";

  // API Endpoints
  static const String loginEndpoint = "$baseUrl/login";
  static const String statusEndpoint = "$baseUrl/status";
  static const String videoStream = "$baseUrl/video_feed";

  // App Strings
  static const String appName = "Smart Retail Guard";
  static const String adminRole = "admin";
}
