import { StyleSheet, Text, View } from "react-native";

import { CircleMember } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

export function MemberPreview({ member }: { member: CircleMember }) {
  return (
    <View style={styles.wrap}>
      <View style={styles.avatar}>
        <Text style={styles.avatarText}>{member.avatar}</Text>
      </View>
      <View style={styles.copy}>
        <Text style={styles.name}>{member.displayName}</Text>
        <Text style={styles.meta}>
          {member.username} · {member.locality}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: 148,
    minHeight: 78,
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    padding: 10,
    gap: 8
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.green,
    alignItems: "center",
    justifyContent: "center"
  },
  avatarText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "900",
    letterSpacing: 0
  },
  copy: {
    gap: 2
  },
  name: {
    color: colors.ink,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  meta: {
    color: colors.inkMuted,
    fontSize: 12,
    lineHeight: 16,
    letterSpacing: 0
  }
});
