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
  { key: "circles", label: "Circulos", icon: "account-group-outline" },
  { key: "align", label: "Alinhar", icon: "calendar-check-outline" },
  { key: "memories", label: "Memorias", icon: "image-multiple-outline" },
  { key: "profile", label: "Perfil", icon: "account-circle-outline" }
];

export function BottomTabs({
  activeTab,
  onChange
}: {
  activeTab: TabKey;
  onChange: (tab: TabKey) => void;
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
            <MaterialCommunityIcons name={icon} size={21} color={color} />
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
