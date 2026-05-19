import { MaterialCommunityIcons } from "@expo/vector-icons";
import { StyleSheet, Text, View } from "react-native";

import { Mission } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";
import { ActionButton } from "./ActionButton";
import { Pill } from "./Pill";

const durationLabel: Record<Mission["durationLabel"], string> = {
  micro: "Micro",
  leve: "Leve",
  realista: "Realista",
  plano: "Plano",
  maior: "Maior"
};

const modeLabel: Record<Mission["mode"], string> = {
  coragem: "Coragem",
  social: "Social",
  familia: "Familia",
  saude: "Saude",
  recomeco: "Recomeco"
};

const intensityLabel: Record<Mission["intensity"], string> = {
  leve: "Leve",
  real: "Real",
  coragem: "Coragem"
};

export function MissionCard({
  mission,
  onAccept,
  onNotToday
}: {
  mission: Mission;
  onAccept: () => void;
  onNotToday: () => void;
}) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.pills}>
          <Pill tone="green">{modeLabel[mission.mode]}</Pill>
          <Pill tone="gold">{durationLabel[mission.durationLabel]}</Pill>
          <Pill tone="blue">{mission.estimatedMinutes} min</Pill>
        </View>
        <Pill tone={mission.intensity === "coragem" ? "coral" : "muted"}>
          {intensityLabel[mission.intensity]}
        </Pill>
      </View>

      <Text style={styles.title}>{mission.title}</Text>
      <Text style={styles.description}>{mission.description}</Text>

      <View style={styles.detailBox}>
        <View style={styles.detailRow}>
          <MaterialCommunityIcons
            name="clock-outline"
            size={17}
            color={colors.blue}
          />
          <Text style={styles.detailText}>
            Tempo previsto: {mission.estimatedMinutes} minutos
          </Text>
        </View>
        <View style={styles.detailRow}>
          <MaterialCommunityIcons
            name="shield-check-outline"
            size={17}
            color={colors.green}
          />
          <Text style={styles.detailText}>{mission.accessibilityNote}</Text>
        </View>
        <View style={styles.detailRow}>
          <MaterialCommunityIcons
            name="hand-heart-outline"
            size={17}
            color={colors.coral}
          />
          <Text style={styles.detailText}>{mission.reason}</Text>
        </View>
      </View>

      <View style={styles.actions}>
        <ActionButton onPress={onAccept} style={styles.actionGrow}>
          Aceitar
        </ActionButton>
        <ActionButton variant="secondary" style={styles.actionGrow}>
          Convidar
        </ActionButton>
      </View>
      <View style={styles.actions}>
        <ActionButton variant="secondary" style={styles.actionGrow}>
          Quem alinha?
        </ActionButton>
        <ActionButton
          onPress={onNotToday}
          variant="ghost"
          style={styles.actionGrow}
        >
          Hoje nao da
        </ActionButton>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 18,
    gap: 14,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.16,
    shadowRadius: 18,
    elevation: 2
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 10
  },
  pills: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 7,
    flex: 1
  },
  title: {
    color: colors.ink,
    fontSize: 28,
    lineHeight: 33,
    fontWeight: "900",
    letterSpacing: 0
  },
  description: {
    color: colors.inkMuted,
    fontSize: 16,
    lineHeight: 23,
    letterSpacing: 0
  },
  detailBox: {
    backgroundColor: colors.background,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 12,
    gap: 10
  },
  detailRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 9
  },
  detailText: {
    color: colors.ink,
    flex: 1,
    fontSize: 14,
    lineHeight: 19,
    letterSpacing: 0
  },
  actions: {
    flexDirection: "row",
    gap: 10
  },
  actionGrow: {
    flex: 1
  }
});
