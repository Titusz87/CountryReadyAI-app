import 'package:flutter/material.dart';
import '../../widgets/guess_mode/guess_mode_header.dart';
import '../../widgets/household/current_alert_card.dart';
import '../../widgets/household/household_status_card.dart';
import '../../widgets/household/preparedness_card.dart';
import '../../widgets/household/community_updates_card.dart';
import '../login_page.dart';

//import 'package:maplibre_gl/maplibre_gl.dart';

class GuessModeDashboard extends StatelessWidget {
  const GuessModeDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CountryReady.ai'),
        centerTitle: true,
      ),
/*
      body: MapLibreMap(
        initialCameraPosition: const CameraPosition(
          target: LatLng(-25.2744, 133.7751),
          zoom: 2.5,
        ),
        styleString: 'https://tiles.openfreemap.org/styles/dark',
      ),
*/
     body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: const [
            GuessModeHeader(),

            SizedBox(height: 20),
            /*

            CurrentAlertCard(),

            SizedBox(height: 16),

            HouseholdStatusCard(),

            SizedBox(height: 16),
            

            PreparednessCard(),

            SizedBox(height: 16),

            CommunityUpdatesCard(),
            */
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: 0,
        onDestinationSelected: (index) {
    if (index == 2) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => const LoginPage(),
        ),
      );
    }
  },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.warning),
            label: 'Incidents',
          ),
          NavigationDestination(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}