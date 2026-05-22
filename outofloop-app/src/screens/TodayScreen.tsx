import { useEffect, useMemo, useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { MissionCard } from "../components/MissionCard";
import { SmartHint } from "../components/SmartHint";
import { Mission, selectMissionOfTheDay } from "../data/missions.generated";
import { AppPreferences } from "../data/preferences";
import { colors, radius } from "../theme/colors";

export function TodayScreen({
  preferences,
  onMissionComplete
}: {
  preferences: AppPreferences;
  onMissionComplete: (mission: Mission) => void;
}) {
  const [accepted, setAccepted] = useState(false);
  const [acceptedAt, setAcceptedAt] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const [notTodayOpen, setNotTodayOpen] = useState(false);
  const [completionOpen, setCompletionOpen] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [congratsOpen, setCongratsOpen] = useState(false);
  const [completionResult, setCompletionResult] = useState<string | null>(null);
  const [feedbackResult, setFeedbackResult] = useState<string | null>(null);
  const [memorySaved, setMemorySaved] = useState(false);
  const todayMission = selectMissionOfTheDay(preferences);
  const minuteLabel =
    todayMission.estimatedMinutes === 1
      ? "1 minuto"
      : `${todayMission.estimatedMinutes} minutos`;
  const timerTotalSeconds = todayMission.estimatedMinutes * 60;
  const timerRemainingSeconds = useMemo(() => {
    if (!acceptedAt || completed) {
      return timerTotalSeconds;
    }

    const elapsedSeconds = Math.floor((now - acceptedAt) / 1000);
    return Math.max(timerTotalSeconds - elapsedSeconds, 0);
  }, [acceptedAt, completed, now, timerTotalSeconds]);
  const timerProgress =
    timerTotalSeconds === 0
      ? 1
      : (timerTotalSeconds - timerRemainingSeconds) / timerTotalSeconds;
  const timerMinutes = Math.floor(timerRemainingSeconds / 60);
  const timerSeconds = timerRemainingSeconds % 60;
  const timerLabel = `${timerMinutes}:${String(timerSeconds).padStart(2, "0")}`;

  useEffect(() => {
    if (!accepted || completed) {
      return;
    }

    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, [accepted, completed]);

  function acceptMission() {
    setAccepted(true);
    setAcceptedAt(Date.now());
    setNow(Date.now());
  }

  function confirmCompletion(result: string) {
    setCompletionResult(result);
    setCompletionOpen(false);
    setCompleted(true);
    onMissionComplete(todayMission);
    setFeedbackOpen(true);
  }

  function finishFeedback(result: string) {
    setFeedbackResult(result);
    setFeedbackOpen(false);
    setCongratsOpen(true);
  }

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>Hoje vamos pequeno</Text>
        <Text style={styles.heading}>Sai do loop por {minuteLabel}.</Text>
        <Text style={styles.subheading}>
          Uma missao simples, sem culpa e com tempo claro.
        </Text>
      </View>

      {completed ? (
        <View style={styles.completedCard}>
          <Text style={styles.completedLabel}>Missao concluida</Text>
          <Text style={styles.completedTitle}>{todayMission.title}</Text>
          <Text style={styles.completedText}>
            Isto ja conta: fizeste uma coisa fora da rotina.
          </Text>
          {feedbackResult ? (
            <Text style={styles.completedMeta}>Feedback: {feedbackResult}</Text>
          ) : null}
          {completionResult ? (
            <Text style={styles.completedMeta}>
              Confirmacao: {completionResult}
            </Text>
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
              setAcceptedAt(null);
              setCompleted(false);
              setCompletionResult(null);
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
            Faz isto ate ao fim do dia. Se nao der, podes ajustar sem culpa.
          </Text>
          <View style={styles.timerBox}>
            <View style={styles.timerTop}>
              <Text style={styles.timerLabel}>Tempo da missao</Text>
              <Text style={styles.timerValue}>
                {timerRemainingSeconds === 0 ? "pronto" : timerLabel}
              </Text>
            </View>
            <View style={styles.progressTrack}>
              <View
                style={[
                  styles.progressFill,
                  { width: `${Math.min(timerProgress * 100, 100)}%` }
                ]}
              />
            </View>
            <Text style={styles.timerHint}>
              {timerRemainingSeconds === 0
                ? "O tempo acabou. Se fizeste, fecha a missao."
                : "O tempo e so uma ajuda, nao uma pressao."}
            </Text>
          </View>
          <View style={styles.acceptedActions}>
            <ActionButton
              onPress={() => setCompletionOpen(true)}
              style={styles.actionGrow}
            >
              {timerRemainingSeconds === 0 ? "Confirmar" : "Concluir"}
            </ActionButton>
            <ActionButton
              variant="secondary"
              onPress={() => {
                setAccepted(false);
                setAcceptedAt(null);
              }}
              style={styles.actionGrow}
            >
              Voltar
            </ActionButton>
          </View>
        </View>
      ) : (
        <>
          {preferences.smartHelp.suggestMissions ? (
            <SmartHint
              title="Ajuda inteligente"
              text={`Esta missao encaixa no teu limite de ${preferences.maxMinutes} minutos e no foco "${todayMission.mode}".`}
            />
          ) : null}
          <MissionCard
            mission={todayMission}
            onAccept={acceptMission}
            onNotToday={() => setNotTodayOpen(true)}
          />
        </>
      )}

      <View style={styles.note}>
        <Text style={styles.noteTitle}>Porque esta missao?</Text>
        <Text style={styles.noteText}>
          {preferences.smartHelp.suggestMissions
            ? "Porque combina com as escolhas que fizeste no Perfil."
            : "Porque uma coisa pequena pode ajudar-te a sair da rotina sem peso."}
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
        visible={completionOpen}
        onRequestClose={() => setCompletionOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalKicker}>Confirmar</Text>
            <Text style={styles.modalTitle}>Cumpriste a missao?</Text>
            <Text style={styles.modalText}>
              Nao precisa de ser perfeito. Queremos saber se tentaste.
            </Text>
            {["Sim, cumpri", "Mais ou menos", "Tentei, mas nao deu"].map(
              (result) => (
                <ActionButton
                  key={result}
                  variant="secondary"
                  onPress={() => confirmCompletion(result)}
                >
                  {result}
                </ActionButton>
              )
            )}
            <ActionButton
              variant="ghost"
              onPress={() => setCompletionOpen(false)}
            >
              Ainda estou a fazer
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
            <Text style={styles.modalKicker}>Feedback rapido</Text>
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
                onPress={() => finishFeedback(result)}
              >
                {result}
              </ActionButton>
            ))}
            <ActionButton
              variant="ghost"
              onPress={() => finishFeedback("Sem feedback")}
            >
              Saltar
            </ActionButton>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="fade"
        transparent
        visible={congratsOpen}
        onRequestClose={() => setCongratsOpen(false)}
      >
        <View style={styles.centerBackdrop}>
          <View style={styles.congratsCard}>
            <Text style={styles.congratsKicker}>Guardado</Text>
            <Text style={styles.congratsTitle}>Boa. Saiste do loop hoje.</Text>
            <Text style={styles.congratsText}>
              Pequeno ou imperfeito, conta. A proxima missao pode adaptar-se a
              isto.
            </Text>
            <ActionButton onPress={() => setCongratsOpen(false)}>
              Fechar
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
  timerBox: {
    backgroundColor: "rgba(255, 255, 255, 0.12)",
    borderRadius: radius.md,
    padding: 14,
    gap: 9
  },
  timerTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "baseline",
    gap: 12
  },
  timerLabel: {
    color: colors.greenSoft,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  timerValue: {
    color: "#FFFFFF",
    fontSize: 26,
    lineHeight: 30,
    fontWeight: "900",
    letterSpacing: 0,
    fontVariant: ["tabular-nums"]
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
  timerHint: {
    color: "#EEF6EF",
    fontSize: 13,
    lineHeight: 18,
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
  modalKicker: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
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
  },
  centerBackdrop: {
    flex: 1,
    justifyContent: "center",
    padding: 24,
    backgroundColor: "rgba(31, 39, 35, 0.44)"
  },
  congratsCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 22,
    gap: 14,
    borderWidth: 1,
    borderColor: colors.line
  },
  congratsKicker: {
    color: colors.green,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  congratsTitle: {
    color: colors.ink,
    fontSize: 28,
    lineHeight: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  congratsText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
