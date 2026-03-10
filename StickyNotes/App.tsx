/**
 * Sticky Notes — React Native (bare, no Expo)
 * Syncs with Linux PC over local WiFi via WebSocket.
 * Saves locally with AsyncStorage when offline.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  StyleSheet,
  View,
  TextInput,
  Text,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
// import Config from 'react-native-config';

// ── Config (values from .env via react-native-config) ─────────────────────────
const WS_PORT = 8765;
const RECONNECT_MS = 4000;

const STORAGE_TEXT = '@sticky:text';
const STORAGE_TS = '@sticky:ts';
const STORAGE_IP = '@sticky:ip';

export default function App() {
  const [text, setText] = useState('');
  const [pcIp, setPcIp] = useState('');
  const [editingIp, setEditingIp] = useState(false);
  const [status, setStatus] = useState('⏳ Connecting…');
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnTimer = useRef<NodeJS.Timeout | null>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const localTsRef = useRef(0);
  const textRef = useRef('');
  const pcIpRef = useRef('');

  // keep pcIpRef in sync so the reconnect closure always uses latest IP
  useEffect(() => { pcIpRef.current = pcIp; }, [pcIp]);

  // ── Load saved note on mount ──────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      const savedText = await AsyncStorage.getItem(STORAGE_TEXT);
      const savedTs = await AsyncStorage.getItem(STORAGE_TS);
      const savedIp = await AsyncStorage.getItem(STORAGE_IP);
      if (savedText !== null) { setText(savedText); textRef.current = savedText; }
      if (savedTs !== null) { localTsRef.current = parseFloat(savedTs); }
      if (savedIp !== null) { setPcIp(savedIp); pcIpRef.current = savedIp; }
    })();
  }, []);

  // ── Persist locally ───────────────────────────────────────────────────────
  const saveLocal = useCallback(async (newText: string, ts: number) => {
    await AsyncStorage.setItem(STORAGE_TEXT, newText);
    await AsyncStorage.setItem(STORAGE_TS, String(ts));
    localTsRef.current = ts;
  }, []);

  // ── WebSocket ─────────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (reconnTimer.current) clearTimeout(reconnTimer.current);
    if (!pcIpRef.current) {
      setStatus('📝 Enter your PC IP above to sync');
      return;
    }
    if (wsRef.current) {
      try { wsRef.current.close(); } catch (_) { }
    }

    const url = `ws://${pcIpRef.current}:${WS_PORT}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setStatus('✅ Synced with PC');
    };

    ws.onmessage = ({ data }) => {
      try {
        const msg = JSON.parse(data);
        if (msg.type === 'update' && msg.ts > localTsRef.current) {
          setText(msg.text);
          textRef.current = msg.text;
          saveLocal(msg.text, msg.ts);
          setStatus('✅ Synced with PC');
        } else if (msg.type === 'ping') {
          ws.send(JSON.stringify({ type: 'pong' }));
        }
      } catch (_) { }
    };

    ws.onerror = () => setStatus("⚠️ Can't reach PC");

    ws.onclose = () => {
      setConnected(false);
      setStatus('📴 Offline — saved locally');
      reconnTimer.current = setTimeout(connect, RECONNECT_MS);
    };
  }, [saveLocal]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnTimer.current) clearTimeout(reconnTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  // ── Text changes → debounced sync ────────────────────────────────────────
  const onChangeText = (newText: string) => {
    setText(newText);
    textRef.current = newText;

    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(async () => {
      const ts = Date.now() / 1000;
      await saveLocal(textRef.current, ts);
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'update', text: textRef.current, ts }));
        setStatus('✅ Synced with PC');
      } else {
        setStatus('📴 Offline — saved locally');
      }
    }, 800);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar backgroundColor="#ffd740" barStyle="dark-content" />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>

        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>📝 Sticky Notes</Text>
          <Text style={styles.statusText}>{status}</Text>
        </View>

        {/* PC IP row */}
        <View style={styles.ipRow}>
          <Text style={styles.ipLabel}>PC IP:</Text>
          <TextInput
            style={styles.ipInput}
            value={pcIp}
            onChangeText={setPcIp}
            onBlur={async () => {
              setEditingIp(false);
              await AsyncStorage.setItem(STORAGE_IP, pcIp);
              connect();
            }}
            onFocus={() => setEditingIp(true)}
            keyboardType="numeric"
            placeholder="Enter PC IP (e.g. 192.168.1.x)"
            placeholderTextColor="#bbb"
          />
          {!connected
            ? <ActivityIndicator size="small" color="#cc4400" style={{ marginLeft: 8 }} />
            : <Text style={styles.dot}>🟢</Text>
          }
        </View>

        {/* Note area */}
        <TextInput
          style={styles.noteInput}
          multiline
          value={text}
          onChangeText={onChangeText}
          placeholder="Start typing your note…"
          placeholderTextColor="#bbb"
          textAlignVertical="top"
          scrollEnabled
        />

      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#fffde7' },
  flex: { flex: 1 },
  header: {
    backgroundColor: '#ffd740',
    paddingTop: 14,
    paddingBottom: 10,
    paddingHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 4,
  },
  title: { fontSize: 18, fontWeight: 'bold', color: '#2b1800' },
  statusText: { fontSize: 11, color: '#555', maxWidth: 170, textAlign: 'right' },
  ipRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff8e1',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#ffe082',
  },
  ipLabel: { fontSize: 12, color: '#888', marginRight: 6 },
  ipInput: {
    flex: 1,
    fontSize: 13,
    color: '#333',
    paddingVertical: 2,
    borderBottomWidth: 1,
    borderBottomColor: '#ffd740',
  },
  dot: { marginLeft: 8, fontSize: 12 },
  noteInput: {
    flex: 1,
    fontSize: 16,
    color: '#1a1a2e',
    padding: 16,
    lineHeight: 24,
    backgroundColor: '#fffde7',
  },
});
