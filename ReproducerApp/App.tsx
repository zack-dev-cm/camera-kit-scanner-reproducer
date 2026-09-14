import { useState } from 'react';
import {
  Button,
  PermissionsAndroid,
  Platform,
  StyleSheet,
  Text,
} from 'react-native';
import { Camera, CameraType } from 'react-native-camera-kit';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

export default function App() {
  const [mounted, setMounted] = useState(false);
  const [events, setEvents] = useState(0);
  const [permission, setPermission] = useState('');
  const start = async () => {
    if (Platform.OS === 'android') {
      const result = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.CAMERA,
      );
      setPermission(result);
      if (result !== PermissionsAndroid.RESULTS.GRANTED) return;
    }
    setEvents(0);
    setMounted(true);
  };
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <Text>Camera Kit scanner ownership reproduction</Text>
        <Text>Camera Kit 18.0.1 / React Native 0.81.0</Text>
        <Text>Barcode callbacks: {events}</Text>
        {mounted ? (
          <>
            <Camera
              style={styles.camera}
              cameraType={CameraType.Back}
              scanBarcode={true}
              onReadCode={() => setEvents(n => n + 1)}
            />
            <Button title="Unmount camera" onPress={() => setMounted(false)} />
          </>
        ) : (
          <Button title="Mount barcode camera" onPress={start} />
        )}
        <Text>{permission}</Text>
        <Text>
          Use the native regression command in README to assert scanner and
          image ownership.
        </Text>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  camera: { flex: 1 },
});
