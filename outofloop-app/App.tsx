import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet, View } from "react-native";

import {
  AlertsScreen,
  alertCountForPlans
} from "./src/screens/AlertsScreen";
import { BottomTabs } from "./src/components/BottomTabs";
import { AlignScreen } from "./src/screens/AlignScreen";
import { CirclesScreen } from "./src/screens/CirclesScreen";
import { MemoriesScreen } from "./src/screens/MemoriesScreen";
import { OnboardingScreen } from "./src/screens/OnboardingScreen";
import { ProfileScreen } from "./src/screens/ProfileScreen";
import { TodayScreen } from "./src/screens/TodayScreen";
import { colors } from "./src/theme/colors";
import { useEffect, useState } from "react";
import { AppMemory } from "./src/data/memories";
import {
  AppPreferences,
  defaultPreferences
} from "./src/data/preferences";
import { upcomingPlans, UpcomingPlan } from "./src/data/mockMissions";
import { Mission } from "./src/data/missions.generated";
import {
  NotificationPreference,
  requestNotificationPermission,
  schedulePlanNotification
} from "./src/data/notifications";
import {
  PlanResponses,
  PlanStatuses,
  PlanStatus
} from "./src/data/planState";
import { buildProgressPath, ProgressPath } from "./src/data/progress";
import {
  readStoredValue,
  writeStoredValue
} from "./src/data/storage";
import { AppUser, defaultUser } from "./src/data/user";

export type TabKey =
  | "today"
  | "alerts"
  | "circles"
  | "align"
  | "memories"
  | "profile";

const storageKeys = {
  onboardingComplete: "outofloop:onboardingComplete",
  user: "outofloop:user",
  notificationPreference: "outofloop:notificationPreference",
  preferences: "outofloop:preferences",
  memories: "outofloop:memories",
  plans: "outofloop:plans",
  planStatuses: "outofloop:planStatuses",
  planResponses: "outofloop:planResponses"
};

function renderScreen(
  tab: TabKey,
  preferences: AppPreferences,
  user: AppUser,
  memories: AppMemory[],
  progress: ProgressPath,
  plans: UpcomingPlan[],
  planStatuses: PlanStatuses,
  planResponses: PlanResponses,
  onCreatePlan: (plan: UpcomingPlan) => void,
  onPlanStatusChange: (planId: string, status: PlanStatus) => void,
  onPlanResponseChange: (planId: string, response: PlanResponses[string]) => void,
  onPlanCheckIn: (plan: UpcomingPlan) => void,
  onMissionComplete: (mission: Mission) => void,
  onMemoryNoteChange: (memoryId: string, note: string) => void,
  onUserChange: (user: AppUser) => void,
  onPreferencesChange: (preferences: AppPreferences) => void,
  onNavigate: (tab: TabKey) => void,
  notificationPreference: NotificationPreference,
  onEnableNotifications: () => void,
  onSendPlanReminder: (plan: UpcomingPlan) => void
) {
  switch (tab) {
    case "alerts":
      return (
        <AlertsScreen
          plans={plans}
          preferences={preferences}
          planStatuses={planStatuses}
          planResponses={planResponses}
          onPlanStatusChange={onPlanStatusChange}
          onPlanResponseChange={onPlanResponseChange}
          onNavigate={onNavigate}
          notificationPreference={notificationPreference}
          onEnableNotifications={onEnableNotifications}
          onSendPlanReminder={onSendPlanReminder}
        />
      );
    case "circles":
      return <CirclesScreen onCreatePlan={onCreatePlan} />;
    case "align":
      return (
        <AlignScreen
          plans={plans}
          preferences={preferences}
          planStatuses={planStatuses}
          planResponses={planResponses}
          onPlanStatusChange={onPlanStatusChange}
          onPlanResponseChange={onPlanResponseChange}
          onCheckIn={onPlanCheckIn}
        />
      );
    case "memories":
      return (
        <MemoriesScreen
          memories={memories}
          onMemoryNoteChange={onMemoryNoteChange}
        />
      );
    case "profile":
      return (
        <ProfileScreen
          preferences={preferences}
          progress={progress}
          user={user}
          onUserChange={onUserChange}
          onPreferencesChange={onPreferencesChange}
        />
      );
    case "today":
    default:
      return (
        <TodayScreen
          preferences={preferences}
          onMissionComplete={onMissionComplete}
        />
      );
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("today");
  const [storageLoaded, setStorageLoaded] = useState(false);
  const [onboardingComplete, setOnboardingComplete] = useState(() =>
    readStoredValue(storageKeys.onboardingComplete, false)
  );
  const [preferences, setPreferences] = useState<AppPreferences>(() => ({
    ...defaultPreferences,
    ...readStoredValue(storageKeys.preferences, defaultPreferences),
    smartHelp: {
      ...defaultPreferences.smartHelp,
      ...readStoredValue(storageKeys.preferences, defaultPreferences).smartHelp
    }
  }));
  const [user, setUser] = useState<AppUser>(() => ({
    ...defaultUser,
    ...readStoredValue(storageKeys.user, defaultUser)
  }));
  const [notificationPreference, setNotificationPreference] =
    useState<NotificationPreference>(() =>
      readStoredValue(storageKeys.notificationPreference, "unknown")
    );
  const [memories, setMemories] = useState<AppMemory[]>(() =>
    readStoredValue(storageKeys.memories, [])
  );
  const [plans, setPlans] = useState<UpcomingPlan[]>(() =>
    readStoredValue(storageKeys.plans, upcomingPlans)
  );
  const [planStatuses, setPlanStatuses] = useState<PlanStatuses>(() =>
    readStoredValue(storageKeys.planStatuses, {})
  );
  const [planResponses, setPlanResponses] = useState<PlanResponses>(() =>
    readStoredValue(storageKeys.planResponses, {})
  );
  const progress = buildProgressPath(memories);
  const alertCount = alertCountForPlans(plans, planStatuses, planResponses);

  useEffect(() => {
    setStorageLoaded(true);
  }, []);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.onboardingComplete, onboardingComplete);
    }
  }, [onboardingComplete, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.preferences, preferences);
    }
  }, [preferences, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.user, user);
    }
  }, [user, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(
        storageKeys.notificationPreference,
        notificationPreference
      );
    }
  }, [notificationPreference, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.memories, memories);
    }
  }, [memories, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.plans, plans);
    }
  }, [plans, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.planStatuses, planStatuses);
    }
  }, [planStatuses, storageLoaded]);

  useEffect(() => {
    if (storageLoaded) {
      writeStoredValue(storageKeys.planResponses, planResponses);
    }
  }, [planResponses, storageLoaded]);

  function handleCreatePlan(plan: UpcomingPlan) {
    setPlans((current) => [plan, ...current]);
    setPlanStatuses((current) => ({
      ...current,
      [plan.id]: "open"
    }));
    setActiveTab("align");
  }

  function handlePlanStatusChange(planId: string, status: PlanStatus) {
    setPlanStatuses((current) => ({
      ...current,
      [planId]: status
    }));
  }

  function handlePlanResponseChange(
    planId: string,
    response: PlanResponses[string]
  ) {
    setPlanResponses((current) => ({
      ...current,
      [planId]: response
    }));
  }

  function handlePlanCheckIn(plan: UpcomingPlan) {
    setMemories((current) => {
      const existing = current.some(
        (memory) => memory.sourceType === "plan" && memory.sourceId === plan.id
      );

      if (existing) {
        return current;
      }

      return [
        {
          id: `memory-${plan.id}`,
          sourceId: plan.id,
          sourceType: "plan",
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

  function handleMissionComplete(mission: Mission) {
    setMemories((current) => {
      const existing = current.some(
        (memory) =>
          memory.sourceType === "mission" && memory.sourceId === mission.slug
      );

      if (existing) {
        return current;
      }

      return [
        {
          id: `memory-mission-${mission.slug}`,
          sourceId: mission.slug,
          sourceType: "mission",
          title: mission.title,
          circle: "Missao privada",
          time: "Hoje",
          place: "No teu ritmo",
          privacy: "private",
          prompt: "O que aconteceu quando saiste da rotina?"
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

  async function handleEnableNotifications() {
    const nextPreference = await requestNotificationPermission();
    setNotificationPreference(nextPreference);
  }

  async function handleSendPlanReminder(plan: UpcomingPlan) {
    if (notificationPreference !== "enabled") {
      const nextPreference = await requestNotificationPermission();
      setNotificationPreference(nextPreference);

      if (nextPreference !== "enabled") {
        return;
      }
    }

    await schedulePlanNotification(plan);
  }

  if (!onboardingComplete) {
    return (
      <SafeAreaView style={styles.safe}>
        <StatusBar style="dark" />
        <OnboardingScreen
          onComplete={(nextPreferences, nextUser) => {
            setPreferences(nextPreferences);
            setUser(nextUser);
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
          user,
          memories,
          progress,
          plans,
          planStatuses,
          planResponses,
          handleCreatePlan,
          handlePlanStatusChange,
          handlePlanResponseChange,
          handlePlanCheckIn,
          handleMissionComplete,
          handleMemoryNoteChange,
          setUser,
          setPreferences,
          setActiveTab,
          notificationPreference,
          handleEnableNotifications,
          handleSendPlanReminder
        )}
      </View>
      <BottomTabs
        activeTab={activeTab}
        onChange={setActiveTab}
        alertCount={alertCount}
      />
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
