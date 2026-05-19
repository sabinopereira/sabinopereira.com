import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { circles } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

export function CirclesScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Os teus circulos</Text>
        <Text style={styles.subtitle}>
          Comunidade privada, pequena e com regras claras.
        </Text>
      </View>

      {circles.map((circle) => (
        <View key={circle.id} style={styles.card}>
          <View style={styles.cardHeader}>
            <View>
              <Text style={styles.cardTitle}>{circle.name}</Text>
              <Text style={styles.meta}>{circle.members} membros</Text>
            </View>
            <Pill tone={circle.role === "Anfitriao" ? "green" : "muted"}>
              {circle.role}
            </Pill>
          </View>
          <Text style={styles.next}>Proximo: {circle.next}</Text>
          <View style={styles.actions}>
            <ActionButton variant="secondary" style={styles.actionGrow}>
              Abrir
            </ActionButton>
            <ActionButton variant="ghost" style={styles.actionGrow}>
              Convidar
            </ActionButton>
          </View>
        </View>
      ))}

      <ActionButton>Criar circulo</ActionButton>
      <ActionButton variant="ghost">Saltar grupos por agora</ActionButton>
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
    gap: 14,
    borderWidth: 1,
    borderColor: colors.line
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: 0
  },
  meta: {
    color: colors.inkMuted,
    fontSize: 13,
    letterSpacing: 0
  },
  next: {
    color: colors.ink,
    fontSize: 15,
    lineHeight: 21,
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
