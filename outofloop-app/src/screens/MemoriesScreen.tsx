import { ScrollView, StyleSheet, Text, TextInput, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { AppMemory } from "../data/memories";
import { colors, radius } from "../theme/colors";

export function MemoriesScreen({
  memories,
  onMemoryNoteChange
}: {
  memories: AppMemory[];
  onMemoryNoteChange: (memoryId: string, note: string) => void;
}) {
  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.header}>
        <Text style={styles.title}>Memorias</Text>
        <Text style={styles.subtitle}>
          O arquivo privado das coisas que realmente aconteceram.
        </Text>
      </View>

      {memories.length === 0 ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyLabel}>Nada para provar</Text>
          <Text style={styles.emptyTitle}>Ainda nao ha memorias.</Text>
          <Text style={styles.emptyText}>
            Quando fizeres check-in num plano em Quem alinha, aparece aqui uma
            memoria para fechares a historia.
          </Text>
        </View>
      ) : (
        memories.map((memory) => (
          <View key={memory.id} style={styles.card}>
            <View style={styles.cardTop}>
              <View style={styles.cardTitleWrap}>
                <Text style={styles.cardTitle}>{memory.title}</Text>
                <Text style={styles.meta}>{memory.circle}</Text>
              </View>
              <Text style={styles.privacy}>
                {memory.privacy === "participants"
                  ? "participantes"
                  : "privado"}
              </Text>
            </View>
            <Text style={styles.detail}>{memory.time}</Text>
            <Text style={styles.detail}>{memory.place}</Text>
            <View style={styles.noteBox}>
              <Text style={styles.prompt}>{memory.prompt}</Text>
              <TextInput
                multiline
                value={memory.note ?? ""}
                onChangeText={(text) => onMemoryNoteChange(memory.id, text)}
                placeholder="Uma frase chega."
                placeholderTextColor={colors.inkMuted}
                style={styles.input}
                textAlignVertical="top"
              />
            </View>
          </View>
        ))
      )}

      <View style={styles.cardMuted}>
        <Text style={styles.cardTitle}>Memorias seguras</Text>
        <Text style={styles.text}>
          Fotos e textos devem ficar acessiveis so a participantes confirmados.
          Nesta beta, isto ainda vive localmente no prototipo.
        </Text>
        <ActionButton variant="secondary">Guardar memoria privada</ActionButton>
      </View>
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
    padding: 18,
    gap: 12,
    borderWidth: 1,
    borderColor: colors.line
  },
  emptyCard: {
    backgroundColor: colors.green,
    borderRadius: radius.lg,
    padding: 18,
    gap: 12
  },
  cardMuted: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.lg,
    padding: 18,
    gap: 10
  },
  cardTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12,
    alignItems: "flex-start"
  },
  cardTitleWrap: {
    flex: 1,
    gap: 4
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0
  },
  emptyLabel: {
    color: colors.greenSoft,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  emptyTitle: {
    color: "#FFFFFF",
    fontSize: 24,
    lineHeight: 28,
    fontWeight: "900",
    letterSpacing: 0
  },
  emptyText: {
    color: "#EEF6EF",
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  meta: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 0
  },
  privacy: {
    color: colors.blue,
    backgroundColor: colors.blueSoft,
    borderRadius: radius.sm,
    overflow: "hidden",
    paddingHorizontal: 9,
    paddingVertical: 5,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0
  },
  detail: {
    color: colors.ink,
    fontSize: 15,
    letterSpacing: 0
  },
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  noteBox: {
    backgroundColor: colors.background,
    borderRadius: radius.md,
    padding: 12,
    gap: 8
  },
  prompt: {
    color: colors.ink,
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 0
  },
  input: {
    minHeight: 82,
    color: colors.ink,
    fontSize: 15,
    lineHeight: 21,
    letterSpacing: 0
  }
});
