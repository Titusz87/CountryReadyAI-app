import 'package:flutter/material.dart';
import 'package:maplibre_gl/maplibre_gl.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.teal,
          brightness: Brightness.dark,
        ),
      ),
      home: Scaffold(
      body: MapLibreMap(
        initialCameraPosition: const CameraPosition(
          target: LatLng(-25.2744, 133.7751),
          zoom: 2.5,
        ),
        styleString: 'https://tiles.openfreemap.org/styles/dark',
      ),
        appBar: AppBar(
          title: const Text('CountryReady.ai'),
          centerTitle: true,
        ),
        bottomNavigationBar: NavigationBar(destinations: [
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
        ],)
      ),
    );
  }
}