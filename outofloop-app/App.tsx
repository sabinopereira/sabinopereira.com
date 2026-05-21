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
import { AppMemory } from "./src/data/memories";
import {
  AppPreferences,
  defaultPreferences
} from "./src/data/preferences";
import { upcomingPlans } from "./src/data/mockMissions";

export type TabKey = "today" | "circles" | "align" | "memories" | "profile";

type Plan = (typeof upcomingPlans)[number];

function renderScreen(
  tab: TabKey,
  preferences: AppPreferences,
  memories: AppMemory[],
  onPlanCheckIn: (plan: Plan) => void,
  onMemoryNoteChange: (memoryId: string, note: string) => void
) {
  switch (tab) {
    case "circles":
      return <CirclesScreen />;
    case "align":
      return <AlignScreen onCheckIn={onPlanCheckIn} />;
    case "memories":
      return (
        <MemoriesScreen
          memories={memories}
          onMemoryNoteChange={onMemoryNoteChange}
        />
      );
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
  const [memories, setMemories] = useState<AppMemory[]>([]);

  function handlePlanCheckIn(plan: Plan) {
    setMemories((current) => {
      const existing = current.some((memory) => memory.planId === plan.id);

      if (existing) {
        return current;
      }

      return [
        {
          id: `memory-${plan.id}`,
          planId: plan.id,
          title: plan.title,
          circle: plan.circle,
          time: plan.time,
          place: plan.place,
          privacy: "participants",
          prompt: "O que queres lembrar deste plano?"
        },
        ...current
      ];
    });
  }

  function handleMemoryNoteChange(memoryId: string, note: string) {
    setMemories((current) =>
      current.map((memory) =>
        memory.id === memoryId
          ? {
              ...memory,
              note
            }
          : memory
      )
    );
  }

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
      <View style={styles.screen}>
        {renderScreen(
          activeTab,
          preferences,
          memories,
          handlePlanCheckIn,
          handleMemoryNoteChange
        )}
      </View>
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
