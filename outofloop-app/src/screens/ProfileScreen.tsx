import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { colors, radius } from "../theme/colors";

const preferences = [
  "Private-first",
  "Missoes micro",
  "Gratis e low cost",
  "Locais calmos",
  "Pequenos grupos"
];

export function ProfileScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Perfil</Text>
        <Text style={styles.subtitle}>
          Ritmo, privacidade, acessibilidade e seguranca.
        </Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O teu ritmo</Text>
        <View style={styles.pills}>
          {preferences.map((item) => (
            <Pill key={item} tone="green">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Hoje nao da</Text>
        <Text style={styles.text}>
          A app adapta as proximas missoes quando falta tempo, energia ou
          encaixe.
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
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
