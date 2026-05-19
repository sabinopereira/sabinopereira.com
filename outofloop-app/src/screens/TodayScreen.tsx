import { useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { MissionCard } from "../components/MissionCard";
import { selectMissionOfTheDay } from "../data/missions.generated";
import { AppPreferences } from "../data/preferences";
import { colors, radius } from "../theme/colors";

export function TodayScreen({
  preferences
}: {
  preferences: AppPreferences;
}) {
  const [accepted, setAccepted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [notTodayOpen, setNotTodayOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [feedbackResult, setFeedbackResult] = useState<string | null>(null);
  const [memorySaved, setMemorySaved] = useState(false);
  const todayMission = selectMissionOfTheDay(preferences);
  const minuteLabel =
    todayMission.estimatedMinutes === 1
      ? "1 minuto"
      : `${todayMission.estimatedMinutes} minutos`;

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>Hoje vamos pequeno</Text>
        <Text style={styles.heading}>Sai do loop por {minuteLabel}.</Text>
        <Text style={styles.subheading}>
          Uma missao simples, sem culpa, com tempo previsto claro.
        </Text>
      </View>

      {completed ? (
        <View style={styles.completedCard}>
          <Text style={styles.completedLabel}>Missao concluida</Text>
          <Text style={styles.completedTitle}>{todayMission.title}</Text>
          <Text style={styles.completedText}>
            Isto ja conta: uma acao real fora do automatico.
          </Text>
          {feedbackResult ? (
            <Text style={styles.completedMeta}>Feedback: {feedbackResult}</Text>
          ) : null}
          <View style={styles.memoryBox}>
            <Text style={styles.memoryTitle}>Memoria privada</Text>
            <Text style={styles.memoryText}>
              Guarda uma frase sobre o que aconteceu. So tu ves isto nesta
              versao.
            </Text>
            <ActionButton
              variant={memorySaved ? "secondary" : "primary"}
              onPress={() => setMemorySaved(true)}
            >
              {memorySaved ? "Memoria guardada" : "Guardar memoria"}
            </ActionButton>
          </View>
          <ActionButton
            variant="secondary"
            onPress={() => {
              setAccepted(false);
              setCompleted(false);
              setFeedbackResult(null);
              setMemorySaved(false);
            }}
          >
            Ver outra vez
          </ActionButton>
        </View>
      ) : accepted ? (
        <View style={styles.acceptedCard}>
          <Text style={styles.acceptedLabel}>Missao aceite</Text>
          <Text style={styles.acceptedTitle}>{todayMission.title}</Text>
          <Text style={styles.acceptedText}>
            Faz isto ate ao fim do dia. Se nao der, podes ajustar sem vergonha.
          </Text>
          <View style={styles.acceptedActions}>
            <ActionButton
              onPress={() => {
                setCompleted(true);
                setFeedbackOpen(true);
              }}
              style={styles.actionGrow}
            >
              Concluir
            </ActionButton>
            <ActionButton
              variant="secondary"
              onPress={() => setAccepted(false)}
              style={styles.actionGrow}
            >
              Voltar
            </ActionButton>
          </View>
        </View>
      ) : (
        <MissionCard
          mission={todayMission}
          onAccept={() => setAccepted(true)}
          onNotToday={() => setNotTodayOpen(true)}
        />
      )}

      <View style={styles.note}>
        <Text style={styles.noteTitle}>Porque esta missao?</Text>
        <Text style={styles.noteText}>
          A primeira beta testa se uma acao pequena consegue criar movimento
          real sem empurrar a pessoa para vergonha ou performance.
        </Text>
      </View>

      <Modal
        animationType="slide"
        transparent
        visible={notTodayOpen}
        onRequestClose={() => setNotTodayOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>Sem stress.</Text>
            <Text style={styles.modalText}>O que falhou hoje?</Text>
            {[
              "Sem tempo",
              "Sem energia",
              "Missao dificil demais",
              "Nao era o tipo certo",
              "Quero guardar para depois",
              "Da-me uma mais leve"
            ].map((reason) => (
              <ActionButton
                key={reason}
                variant="secondary"
                onPress={() => setNotTodayOpen(false)}
              >
                {reason}
              </ActionButton>
            ))}
            <ActionButton variant="ghost" onPress={() => setNotTodayOpen(false)}>
              Voltar
            </ActionButton>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={feedbackOpen}
        onRequestClose={() => setFeedbackOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>Como correu?</Text>
            <Text style={styles.modalText}>
              Isto ajuda a ajustar as proximas missoes.
            </Text>
            {[
              "Gostei",
              "Foi facil",
              "Foi no ponto",
              "Foi demais",
              "Quero mais deste tipo",
              "Nao era para mim"
            ].map((result) => (
              <ActionButton
                key={result}
                variant="secondary"
                onPress={() => {
                  setFeedbackResult(result);
                  setFeedbackOpen(false);
                }}
              >
                {result}
              </ActionButton>
            ))}
            <ActionButton
              variant="ghost"
              onPress={() => {
                setFeedbackResult("Sem feedback");
                setFeedbackOpen(false);
              }}
            >
              Saltar
            </ActionButton>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    paddingBottom: 34,
    gap: 18
  },
  hero: {
    gap: 8,
    paddingTop: 8
  },
  eyebrow: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  heading: {
    color: colors.ink,
    fontSize: 34,
    lineHeight: 38,
    fontWeight: "900",
    letterSpacing: 0
  },
  subheading: {
    color: colors.inkMuted,
    fontSize: 16,
    lineHeight: 23,
    letterSpacing: 0
  },
  acceptedCard: {
    backgroundColor: colors.green,
    borderRadius: radius.lg,
    padding: 20,
    gap: 12
  },
  acceptedLabel: {
    color: colors.greenSoft,
    fontSize: 13,
    fontWeight: "800",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  acceptedTitle: {
    color: "#FFFFFF",
    fontSize: 28,
    lineHeight: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  acceptedText: {
    color: "#EEF6EF",
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  acceptedActions: {
    flexDirection: "row",
    gap: 10
  },
  actionGrow: {
    flex: 1
  },
  completedCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 20,
    gap: 14
  },
  completedLabel: {
    color: colors.green,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  completedTitle: {
    color: colors.ink,
    fontSize: 28,
    lineHeight: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  completedText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  completedMeta: {
    color: colors.blue,
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 0
  },
  memoryBox: {
    backgroundColor: colors.background,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 14,
    gap: 10
  },
  memoryTitle: {
    color: colors.ink,
    fontSize: 16,
    fontWeight: "900",
    letterSpacing: 0
  },
  memoryText: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  note: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.md,
    padding: 15,
    gap: 6
  },
  noteTitle: {
    color: colors.ink,
    fontSize: 15,
    fontWeight: "900",
    letterSpacing: 0
  },
  noteText: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  modalBackdrop: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(31, 39, 35, 0.32)"
  },
  modalCard: {
    backgroundColor: colors.background,
    borderTopLeftRadius: 22,
    borderTopRightRadius: 22,
    padding: 20,
    gap: 10
  },
  modalTitle: {
    color: colors.ink,
    fontSize: 26,
    fontWeight: "900",
    letterSpacing: 0
  },
  modalText: {
    color: colors.inkMuted,
    fontSize: 16,
    marginBottom: 4,
    letterSpacing: 0
  }
});
