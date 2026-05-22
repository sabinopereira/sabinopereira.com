import * as Notifications from "expo-notifications";

import type { UpcomingPlan } from "./mockMissions";

export type NotificationPreference = "unknown" | "enabled" | "disabled";
type PermissionResult = {
  granted?: boolean;
  status?: string;
};

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldPlaySound: false,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true
  })
});

export async function requestNotificationPermission() {
  const existing =
    (await Notifications.getPermissionsAsync()) as PermissionResult;

  if (existing.granted || existing.status === "granted") {
    return "enabled" satisfies NotificationPreference;
  }

  const next =
    (await Notifications.requestPermissionsAsync()) as PermissionResult;
  return next.granted || next.status === "granted"
    ? ("enabled" satisfies NotificationPreference)
    : ("disabled" satisfies NotificationPreference);
}

export async function schedulePlanNotification(plan: UpcomingPlan) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: "Plano a pedir resposta",
      body: `${plan.title} - ${plan.time}`,
      data: {
        planId: plan.id,
        type: "plan"
      }
    },
    trigger: {
      type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
      seconds: 2
    }
  });
}
