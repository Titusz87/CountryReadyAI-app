import 'package:flutter/material.dart';
//import 'package:maplibre_gl/maplibre_gl.dart';

class HouseholdDashboard extends StatelessWidget {
  const HouseholdDashboard({super.key});

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
      bottomNavigationBar: NavigationBar(
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