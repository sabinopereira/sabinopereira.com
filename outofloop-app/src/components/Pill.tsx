import { ReactNode } from "react";
import { StyleSheet, Text, View } from "react-native";

import { colors, radius } from "../theme/colors";

type PillTone = "green" | "blue" | "coral" | "gold" | "muted";

const toneMap: Record<PillTone, { backgroundColor: string; color: string }> = {
  green: { backgroundColor: colors.greenSoft, color: colors.green },
  blue: { backgroundColor: colors.blueSoft, color: colors.blue },
  coral: { backgroundColor: colors.coralSoft, color: colors.coral },
  gold: { backgroundColor: colors.goldSoft, color: colors.gold },
  muted: { backgroundColor: colors.surfaceMuted, color: colors.inkMuted }
};

export function Pill({
  children,
  tone = "muted"
}: {
  children: ReactNode;
  tone?: PillTone;
}) {
  const toneStyle = toneMap[tone];

  return (
    <View style={[styles.pill, { backgroundColor: toneStyle.backgroundColor }]}>
      <Text style={[styles.text, { color: toneStyle.color }]}>{children}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    borderRadius: radius.sm,
    paddingHorizontal: 9,
    paddingVertical: 5
  },
  text: {
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 0
  }
});
