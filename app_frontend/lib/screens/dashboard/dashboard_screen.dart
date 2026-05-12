import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../auth/login_screen.dart';
import '../live_view/live_feed_screen.dart';
import '../alerts/alerts_screen.dart';

// --- MAIN DASHBOARD SCREEN ---
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  int _selectedIndex = 0;
  bool _isSystemPaused = false;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _logout(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (context.mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  void _onBottomNavTapped(int index) {
    setState(() => _selectedIndex = index);
    if (index == 1) {
      Navigator.push(
          context, MaterialPageRoute(builder: (_) => const LiveFeedScreen()));
    } else if (index == 2) {
      Navigator.push(
          context, MaterialPageRoute(builder: (_) => const AlertsScreen()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      bottomNavigationBar: _buildBottomNav(),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildProfileHeader(),
                const SizedBox(height: 20),
                _buildSystemStatusPanel(),
                const SizedBox(height: 20),
                _buildStatsRow(),
                const SizedBox(height: 24),
                const Text("Quick Actions",
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                _buildQuickActionsRow(context),
                const SizedBox(height: 24),
                const Text("System Modules",
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                _buildMainFeatureCards(context),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // 1. TOP SECTION - PROFILE HEADER
  Widget _buildProfileHeader() {
    return Row(
      children: [
        Stack(
          children: [
            const CircleAvatar(
              radius: 24,
              backgroundColor: Color(0xFF2A2A2A),
              child: Icon(Icons.person, color: Colors.white70, size: 28),
            ),
            Positioned(
              bottom: 0,
              right: 0,
              child: Container(
                width: 14,
                height: 14,
                decoration: BoxDecoration(
                  color: const Color(0xFF4CAF50),
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF121212), width: 2),
                ),
              ),
            )
          ],
        ),
        const SizedBox(width: 16),
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("Mahendhiran M.",
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold)),
              Text("System Admin",
                  style: TextStyle(color: Colors.white54, fontSize: 14)),
            ],
          ),
        ),
        IconButton(
          icon: const Badge(
            backgroundColor: Color(0xFFE57373),
            label: Text("3"),
            child:
                Icon(Icons.notifications_none, color: Colors.white, size: 28),
          ),
          onPressed: () {},
        ),
        IconButton(
          icon: const Icon(Icons.logout, color: Colors.white54),
          onPressed: () => _logout(context),
        )
      ],
    );
  }

  // 2. SYSTEM STATUS PANEL (Fixed Opacity Syntax)
  Widget _buildSystemStatusPanel() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              // NEW FLUTTER SYNTAX: .withValues(alpha: X)
              color: _isSystemPaused
                  ? Colors.orange.withValues(alpha: 0.1)
                  : const Color(0xFF4CAF50).withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.security,
                color:
                    _isSystemPaused ? Colors.orange : const Color(0xFF4CAF50),
                size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      _isSystemPaused ? "Monitoring Paused" : "System Online",
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    if (!_isSystemPaused)
                      FadeTransition(
                        opacity: _pulseController,
                        child: Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                                color: Color(0xFF4CAF50),
                                shape: BoxShape.circle)),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text("Last sync: Just now",
                    style: TextStyle(color: Colors.white54, fontSize: 12)),
              ],
            ),
          ),
          IconButton(
            icon: Icon(
                _isSystemPaused
                    ? Icons.play_arrow_rounded
                    : Icons.pause_circle_filled,
                color: _isSystemPaused ? Colors.greenAccent : Colors.white54,
                size: 32),
            onPressed: () {
              setState(() => _isSystemPaused = !_isSystemPaused);
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: Text(_isSystemPaused
                    ? "System Monitoring Paused"
                    : "System Monitoring Resumed"),
                backgroundColor: const Color(0xFF1E1E1E),
              ));
            },
          )
        ],
      ),
    );
  }

  // 3. STATS ROW (Added 'const' to the entire Row for max performance)
  Widget _buildStatsRow() {
    return const Row(
      children: [
        Expanded(
            child: _StatCard(
                icon: Icons.videocam,
                value: "4",
                label: "Cams Active",
                color: Colors.blueAccent)),
        SizedBox(width: 12),
        Expanded(
            child: _StatCard(
                icon: Icons.warning_amber_rounded,
                value: "2",
                label: "Alerts Today",
                color: Color(0xFFE57373))),
        SizedBox(width: 12),
        Expanded(
            child: _StatCard(
                icon: Icons.health_and_safety,
                value: "98%",
                label: "Sys Health",
                color: Color(0xFF4CAF50))),
      ],
    );
  }

  // 4. QUICK ACTIONS
  Widget _buildQuickActionsRow(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _QuickActionButton(
            icon: Icons.play_circle_fill,
            label: "Live",
            onTap: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const LiveFeedScreen()))),
        _QuickActionButton(
            icon: Icons.history,
            label: "Replays",
            onTap: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const AlertsScreen()))),
        _QuickActionButton(icon: Icons.bar_chart, label: "Logs", onTap: () {}),
        _QuickActionButton(
            icon: Icons.settings, label: "Settings", onTap: () {}),
      ],
    );
  }

  // 5. MAIN FEATURE CARDS
  Widget _buildMainFeatureCards(BuildContext context) {
    return Column(
      children: [
        _MainFeatureCard(
          icon: Icons.videocam_outlined,
          title: "Live Feed Viewer",
          subtitle: "View real-time YOLOv8 bounding boxes",
          accentColor: Colors.blueAccent,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const LiveFeedScreen())),
        ),
        const SizedBox(height: 16),
        _MainFeatureCard(
          icon: Icons.replay_circle_filled_outlined,
          title: "Theft Replays & Alerts",
          subtitle: "Review flagged sequences and events",
          accentColor: const Color(0xFFE57373),
          onTap: () => Navigator.push(
              context, MaterialPageRoute(builder: (_) => const AlertsScreen())),
        ),
        const SizedBox(height: 16),
        _MainFeatureCard(
          icon: Icons.settings_outlined,
          title: "System Settings",
          subtitle: "Configure AI thresholds and ROIs",
          accentColor: Colors.grey,
          onTap: () {
            ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("Settings Module Opening...")));
          },
        ),
      ],
    );
  }

  // 6. BOTTOM NAVIGATION BAR
  Widget _buildBottomNav() {
    return Container(
      decoration: const BoxDecoration(
        borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20), topRight: Radius.circular(20)),
        boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 10)],
      ),
      child: ClipRRect(
        borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(20), topRight: Radius.circular(20)),
        child: BottomNavigationBar(
          backgroundColor: const Color(0xFF1E1E1E),
          type: BottomNavigationBarType.fixed,
          currentIndex: _selectedIndex,
          selectedItemColor: Colors.white,
          unselectedItemColor: Colors.white38,
          showSelectedLabels: true,
          showUnselectedLabels: false,
          onTap: _onBottomNavTapped,
          items: const [
            BottomNavigationBarItem(
                icon: Icon(Icons.dashboard), label: "Dashboard"),
            BottomNavigationBarItem(icon: Icon(Icons.videocam), label: "Live"),
            BottomNavigationBarItem(
                icon: Icon(Icons.notifications), label: "Alerts"),
            BottomNavigationBarItem(icon: Icon(Icons.person), label: "Profile"),
          ],
        ),
      ),
    );
  }
}

// --- CUSTOM REUSABLE WIDGETS ---

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatCard(
      {required this.icon,
      required this.value,
      required this.label,
      required this.color});

  @override
  Widget build(BuildContext context) {
    return BouncingCard(
      onTap: () {},
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(16),
          boxShadow: const [
            BoxShadow(
                color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(value,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(label,
                style: const TextStyle(color: Colors.white54, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickActionButton(
      {required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return BouncingCard(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF1E1E1E),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(icon, color: Colors.white, size: 28),
          ),
          const SizedBox(height: 8),
          Text(label,
              style: const TextStyle(color: Colors.white70, fontSize: 13)),
        ],
      ),
    );
  }
}

class _MainFeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color accentColor;
  final VoidCallback onTap;

  const _MainFeatureCard(
      {required this.icon,
      required this.title,
      required this.subtitle,
      required this.accentColor,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return BouncingCard(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(16),
          boxShadow: const [
            BoxShadow(
                color: Colors.black12, blurRadius: 8, offset: Offset(0, 4))
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              // NEW FLUTTER SYNTAX: .withValues(alpha: X)
              decoration: BoxDecoration(
                  color: accentColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12)),
              child: Icon(icon, color: accentColor, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(subtitle,
                      style:
                          const TextStyle(color: Colors.white54, fontSize: 13)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.white38),
          ],
        ),
      ),
    );
  }
}

class BouncingCard extends StatefulWidget {
  final Widget child;
  final VoidCallback onTap;

  const BouncingCard({super.key, required this.child, required this.onTap});

  @override
  State<BouncingCard> createState() => _BouncingCardState();
}

class _BouncingCardState extends State<BouncingCard>
    with SingleTickerProviderStateMixin {
  late double _scale;
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 100),
        lowerBound: 0.0,
        upperBound: 0.05)
      ..addListener(() {
        setState(() {});
      });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _tapDown(TapDownDetails details) => _controller.forward();
  void _tapUp(TapUpDetails details) {
    _controller.reverse();
    widget.onTap();
  }

  void _tapCancel() => _controller.reverse();

  @override
  Widget build(BuildContext context) {
    _scale = 1 - _controller.value;
    return GestureDetector(
      onTapDown: _tapDown,
      onTapUp: _tapUp,
      onTapCancel: _tapCancel,
      child: Transform.scale(scale: _scale, child: widget.child),
    );
  }
}
