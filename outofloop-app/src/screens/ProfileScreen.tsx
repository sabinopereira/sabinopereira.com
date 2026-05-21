import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { AppPreferences } from "../data/preferences";
import { ProgressPath } from "../data/progress";
import { colors, radius } from "../theme/colors";

const modeLabel: Record<AppPreferences["primaryMode"], string> = {
  coragem: "Aventura",
  social: "Social",
  familia: "Familia",
  saude: "Saude",
  recomeco: "Recuperar ritmo"
};

const costLabel: Record<AppPreferences["preferredCostTier"], string> = {
  gratis: "Gratis",
  low_cost: "Low cost",
  medio: "Medio",
  especial: "Especial"
};

const intensityLabel: Record<AppPreferences["preferredIntensity"], string> = {
  leve: "Leve",
  real: "Real",
  coragem: "Aventura"
};

export function ProfileScreen({
  preferences,
  progress
}: {
  preferences: AppPreferences;
  progress: ProgressPath;
}) {
  const rhythmChoices = [
    preferences.privateFirst ? "Comecar sozinho/a" : "Comecar com pessoas",
    `${preferences.maxMinutes} min maximo`,
    costLabel[preferences.preferredCostTier],
    intensityLabel[preferences.preferredIntensity],
    modeLabel[preferences.primaryMode],
    preferences.hasChildren ? "Tenho filhos" : null,
    ...preferences.accessibility
  ].filter(Boolean);

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Perfil</Text>
        <Text style={styles.subtitle}>
          O teu ritmo, as tuas escolhas e a tua seguranca.
        </Text>
      </View>
      <View style={styles.pathCard}>
        <Text style={styles.pathKicker}>O teu caminho</Text>
        <Text style={styles.pathTitle}>{progress.currentStage}</Text>
        <Text style={styles.pathText}>{progress.label}</Text>
        <View style={styles.progressTrack}>
          <View
            style={[
              styles.progressFill,
              { width: `${Math.round(progress.progressRatio * 100)}%` }
            ]}
          />
        </View>
        <Text style={styles.pathHint}>
          {progress.nextStage && progress.nextTarget
            ? `Proximo: ${progress.nextStage} aos ${progress.nextTarget} momentos.`
            : "Caminho aberto. Agora podes ajudar outros a entrar."}
        </Text>
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.missionCount}</Text>
            <Text style={styles.statLabel}>missoes</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.planCount}</Text>
            <Text style={styles.statLabel}>planos</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.completedCount}</Text>
            <Text style={styles.statLabel}>momentos</Text>
          </View>
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Marcos</Text>
        <View style={styles.milestones}>
          {progress.milestones.map((milestone) => (
            <View key={milestone.label} style={styles.milestone}>
              <Text
                style={[
                  styles.milestoneMark,
                  !milestone.unlocked && styles.milestoneLocked
                ]}
              >
                {milestone.unlocked ? "OK" : "--"}
              </Text>
              <Text
                style={[
                  styles.milestoneText,
                  !milestone.unlocked && styles.milestoneLocked
                ]}
              >
                {milestone.label}
              </Text>
            </View>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O que queres mexer</Text>
        <View style={styles.pills}>
          {preferences.routineFocus.map((item) => (
            <Pill key={item} tone="green">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O teu ritmo</Text>
        <View style={styles.pills}>
          {rhythmChoices.map((item) => (
            <Pill key={item} tone="blue">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Hoje nao da</Text>
        <Text style={styles.text}>
          A app adapta as proximas missoes quando falta tempo, energia ou
          vontade.
        </Text>
      </View>
      <ActionButton variant="secondary">Pausar missoes</ActionButton>
      <ActionButton variant="ghost">Seguranca e bloqueios</ActionButton>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    gap: 14
  },
  header: {
    gap: 8
  },
  title: {
    color: colors.ink,
    fontSize: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  subtitle: {
    color: colors.inkMuted,
    fontSize: 16,
    lineHeight: 23,
    letterSpacing: 0
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 18,
    gap: 12,
    borderWidth: 1,
    borderColor: colors.line
  },
  pathCard: {
    backgroundColor: colors.green,
    borderRadius: radius.lg,
    padding: 18,
    gap: 12
  },
  pathKicker: {
    color: colors.greenSoft,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  pathTitle: {
    color: "#FFFFFF",
    fontSize: 30,
    lineHeight: 34,
    fontWeight: "900",
    letterSpacing: 0
  },
  pathText: {
    color: "#EEF6EF",
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  progressTrack: {
    height: 8,
    backgroundColor: "rgba(255, 255, 255, 0.22)",
    borderRadius: radius.sm,
    overflow: "hidden"
  },
  progressFill: {
    height: 8,
    backgroundColor: colors.goldSoft,
    borderRadius: radius.sm
  },
  pathHint: {
    color: "#EEF6EF",
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  statsRow: {
    flexDirection: "row",
    gap: 10
  },
  statBox: {
    flex: 1,
    backgroundColor: "rgba(255, 255, 255, 0.12)",
    borderRadius: radius.sm,
    padding: 10,
    gap: 2
  },
  statNumber: {
    color: "#FFFFFF",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0,
    fontVariant: ["tabular-nums"]
  },
  statLabel: {
    color: colors.greenSoft,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: 0
  },
  pills: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  milestones: {
    gap: 10
  },
  milestone: {
    flexDirection: "row",
    gap: 10,
    alignItems: "center"
  },
  milestoneMark: {
    color: colors.green,
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    overflow: "hidden",
    paddingHorizontal: 8,
    paddingVertical: 4,
    fontSize: 12,
    fontWeight: "900",
    letterSpacing: 0
  },
  milestoneText: {
    flex: 1,
    color: colors.ink,
    fontSize: 15,
    lineHeight: 20,
    fontWeight: "700",
    letterSpacing: 0
  },
  milestoneLocked: {
    color: colors.inkMuted
  },
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
