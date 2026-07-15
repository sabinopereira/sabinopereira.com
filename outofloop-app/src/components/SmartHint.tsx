import { MaterialCommunityIcons } from "@expo/vector-icons";
import { StyleSheet, Text, View } from "react-native";

import { colors, radius } from "../theme/colors";

export function SmartHint({
  title,
  text
}: {
  title: string;
  text: string;
}) {
  return (
    <View style={styles.wrap}>
      <MaterialCommunityIcons
        name="creation"
        size={18}
        color={colors.gold}
      />
      <View style={styles.copy}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    backgroundColor: colors.goldSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 9,
    flexDirection: "row",
    alignItems: "flex-start"
  },
  copy: {
    flex: 1,
    gap: 3
  },
  title: {
    color: colors.gold,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  text: {
    color: colors.ink,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  }
});
