import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { upcomingPlans } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

export function AlignScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Quem alinha?</Text>
        <Text style={styles.subtitle}>
          Planos dos teus circulos, com prazo, custo e acessibilidade antes de
          aceitares.
        </Text>
      </View>

      {upcomingPlans.map((plan) => (
        <View key={plan.id} style={styles.card}>
          <View style={styles.row}>
            <Pill tone="green">{plan.costTier}</Pill>
            <Pill tone="blue">{plan.durationLabel}</Pill>
          </View>
          <Text style={styles.cardTitle}>{plan.title}</Text>
          <Text style={styles.meta}>{plan.circle}</Text>
          <Text style={styles.detail}>{plan.time}</Text>
          <Text style={styles.detail}>{plan.place}</Text>
          <Text style={styles.accessibility}>{plan.accessibility}</Text>
          <Text style={styles.deadline}>
            {plan.participants} alinharam, {plan.deadline}
          </Text>
          <ActionButton>Alinhar</ActionButton>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    gap: 14
  },
  header: {
    gap: 8,
    marginBottom: 4
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
    padding: 16,
    gap: 10,
    borderWidth: 1,
    borderColor: colors.line
  },
  row: {
    flexDirection: "row",
    gap: 8
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0
  },
  meta: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 0
  },
  detail: {
    color: colors.ink,
    fontSize: 15,
    letterSpacing: 0
  },
  accessibility: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  deadline: {
    color: colors.blue,
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 0
  }
});
