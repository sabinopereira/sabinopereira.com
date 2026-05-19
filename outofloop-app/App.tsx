import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet, View } from "react-native";

import { BottomTabs } from "./src/components/BottomTabs";
import { AlignScreen } from "./src/screens/AlignScreen";
import { CirclesScreen } from "./src/screens/CirclesScreen";
import { MemoriesScreen } from "./src/screens/MemoriesScreen";
import { OnboardingScreen } from "./src/screens/OnboardingScreen";
import { ProfileScreen } from "./src/screens/ProfileScreen";
import { TodayScreen } from "./src/screens/TodayScreen";
import { colors } from "./src/theme/colors";
import { useState } from "react";
import {
  AppPreferences,
  defaultPreferences
} from "./src/data/preferences";

export type TabKey = "today" | "circles" | "align" | "memories" | "profile";

function renderScreen(tab: TabKey, preferences: AppPreferences) {
  switch (tab) {
    case "circles":
      return <CirclesScreen />;
    case "align":
      return <AlignScreen />;
    case "memories":
      return <MemoriesScreen />;
    case "profile":
      return <ProfileScreen />;
    case "today":
    default:
      return <TodayScreen preferences={preferences} />;
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("today");
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [preferences, setPreferences] =
    useState<AppPreferences>(defaultPreferences);

  if (!onboardingComplete) {
    return (
      <SafeAreaView style={styles.safe}>
        <StatusBar style="dark" />
        <OnboardingScreen
          onComplete={(nextPreferences) => {
            setPreferences(nextPreferences);
            setOnboardingComplete(true);
          }}
        />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="dark" />
      <View style={styles.screen}>{renderScreen(activeTab, preferences)}</View>
      <BottomTabs activeTab={activeTab} onChange={setActiveTab} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background
  },
  screen: {
    flex: 1
  }
});
