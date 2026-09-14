/**
 * @format
 */

import React from 'react';
import ReactTestRenderer from 'react-test-renderer';
import App from '../App';

// The existing template render check does not exercise native camera code.
jest.mock('react-native-camera-kit', () => ({
  Camera: 'Camera',
  CameraType: {Back: 'back'},
}));

test('renders correctly', async () => {
  await ReactTestRenderer.act(() => {
    ReactTestRenderer.create(<App />);
  });
});
