import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { colors, radius } from "../theme/colors";

export function MemoriesScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Text style={styles.title}>Memorias</Text>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Fecha o dia com uma memoria</Text>
        <Text style={styles.text}>
          As memorias podem ser privadas ou partilhadas apenas com quem
          participou no evento.
        </Text>
        <ActionButton>Guardar memoria privada</ActionButton>
      </View>
      <View style={styles.cardMuted}>
        <Text style={styles.cardTitle}>Depois do evento</Text>
        <Text style={styles.text}>
          Fotos e textos ficam acessiveis so a participantes confirmados.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    gap: 14
  },
  title: {
    color: colors.ink,
    fontSize: 32,
    fontWeight: "900",
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
  cardMuted: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.lg,
    padding: 18,
    gap: 10
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0
  },
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
