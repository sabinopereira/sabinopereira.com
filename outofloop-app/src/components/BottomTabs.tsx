import { MaterialCommunityIcons } from "@expo/vector-icons";
import { Pressable, StyleSheet, Text, View } from "react-native";

import type { TabKey } from "../../App";
import { colors } from "../theme/colors";

const tabs: Array<{
  key: TabKey;
  label: string;
  icon: keyof typeof MaterialCommunityIcons.glyphMap;
}> = [
  { key: "today", label: "Hoje", icon: "home-outline" },
  { key: "alerts", label: "Avisos", icon: "bell-outline" },
  { key: "circles", label: "Circulos", icon: "account-group-outline" },
  { key: "align", label: "Alinhar", icon: "calendar-check-outline" },
  { key: "memories", label: "Memorias", icon: "image-multiple-outline" },
  { key: "profile", label: "Perfil", icon: "account-circle-outline" }
];

export function BottomTabs({
  activeTab,
  onChange,
  alertCount = 0
}: {
  activeTab: TabKey;
  onChange: (tab: TabKey) => void;
  alertCount?: number;
}) {
  return (
    <View style={styles.wrap}>
      {tabs.map(({ key, label, icon }) => {
        const active = key === activeTab;
        const color = active ? colors.green : colors.inkMuted;
        return (
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={label}
            key={key}
            onPress={() => onChange(key)}
            style={[styles.tab, active && styles.activeTab]}
          >
            <View style={styles.iconWrap}>
              <MaterialCommunityIcons name={icon} size={21} color={color} />
              {key === "alerts" && alertCount > 0 ? (
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>
                    {alertCount > 9 ? "9+" : alertCount}
                  </Text>
                </View>
              ) : null}
            </View>
            <Text style={[styles.label, active && styles.activeLabel]}>
              {label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: "row",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    backgroundColor: colors.surface,
    paddingHorizontal: 8,
    paddingTop: 8,
    paddingBottom: 12
  },
  tab: {
    flex: 1,
    minHeight: 54,
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    borderRadius: 8
  },
  activeTab: {
    backgroundColor: colors.greenSoft
  },
  iconWrap: {
    width: 26,
    height: 23,
    alignItems: "center",
    justifyContent: "center"
  },
  badge: {
    position: "absolute",
    top: -5,
    right: -8,
    minWidth: 17,
    height: 17,
    borderRadius: 9,
    backgroundColor: colors.coral,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 4
  },
  badgeText: {
    color: "#FFFFFF",
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 0,
    fontVariant: ["tabular-nums"]
  },
  label: {
    color: colors.inkMuted,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0
  },
  activeLabel: {
    color: colors.green
  }
});
