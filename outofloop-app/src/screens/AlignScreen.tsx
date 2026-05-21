import { useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { UpcomingPlan } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

type PlanStatus = "open" | "accepted" | "checkedIn" | "dismissed";
type PlanResponse = {
  detailsViews?: number;
  notNowReason?: string;
};

const notNowReasons = [
  "Hora dificil",
  "Dia nao ajuda",
  "Fica longe",
  "Custo alto",
  "Sem energia",
  "Prefiro algo mais leve"
];

export function AlignScreen({
  plans,
  onCheckIn
}: {
  plans: UpcomingPlan[];
  onCheckIn: (plan: UpcomingPlan) => void;
}) {
  const [planStatuses, setPlanStatuses] = useState<Record<string, PlanStatus>>(
    {}
  );
  const [selectedPlan, setSelectedPlan] = useState<UpcomingPlan | null>(null);
  const [detailsPlan, setDetailsPlan] = useState<UpcomingPlan | null>(null);
  const [notNowPlan, setNotNowPlan] = useState<UpcomingPlan | null>(null);
  const [planResponses, setPlanResponses] = useState<
    Record<string, PlanResponse>
  >({});

  function statusFor(planId: string): PlanStatus {
    return planStatuses[planId] ?? "open";
  }

  function updateStatus(planId: string, status: PlanStatus) {
    setPlanStatuses((current) => ({
      ...current,
      [planId]: status
    }));
  }

  function dismissPlan(planId: string, reason: string) {
    setPlanResponses((current) => ({
      ...current,
      [planId]: {
        ...current[planId],
        notNowReason: reason
      }
    }));
    updateStatus(planId, "dismissed");
    setNotNowPlan(null);
  }

  function openDetails(plan: UpcomingPlan) {
    setPlanResponses((current) => ({
      ...current,
      [plan.id]: {
        ...current[plan.id],
        detailsViews: (current[plan.id]?.detailsViews ?? 0) + 1
      }
    }));
    setDetailsPlan(plan);
  }

  function suggestionFor(reason?: string) {
    switch (reason) {
      case "Hora dificil":
        return "Sugestao: propor duas horas alternativas antes de fechar.";
      case "Dia nao ajuda":
        return "Sugestao: testar outro dia ou transformar em plano de fim de semana.";
      case "Fica longe":
        return "Sugestao: escolher um ponto mais central ou opcao perto de transportes.";
      case "Custo alto":
        return "Sugestao: trocar por opcao gratis ou low cost.";
      case "Sem energia":
      case "Prefiro algo mais leve":
        return "Sugestao: reduzir duracao e deixar claro que sair cedo e ok.";
      default:
        return "Sugestao: manter o plano simples e pedir uma resposta clara.";
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Quem alinha?</Text>
        <Text style={styles.subtitle}>
          Planos dos teus circulos, com prazo, custo e acessibilidade antes de
          aceitares.
        </Text>
      </View>

      {plans.map((plan) => {
        const status = statusFor(plan.id);
        const acceptedCount =
          status === "open" ? plan.acceptedCount : plan.acceptedCount + 1;
        const statusLabel =
          status === "checkedIn"
            ? "check-in feito"
            : status === "accepted"
              ? "alinhado"
              : status === "dismissed"
                ? "agora nao"
                : "aberto";
        const response = planResponses[plan.id];
        const seenCount = Math.min(
          plan.capacity,
          plan.acceptedCount + (response?.detailsViews ?? 0) + 1
        );

        return (
          <View key={plan.id} style={styles.card}>
            <View style={styles.row}>
              <Pill tone="green">{plan.costTier}</Pill>
              <Pill tone="blue">{plan.durationLabel}</Pill>
              <Pill tone={status === "open" ? "muted" : "coral"}>
                {statusLabel}
              </Pill>
            </View>
            <Text style={styles.cardTitle}>{plan.title}</Text>
            <Text style={styles.meta}>{plan.circle}</Text>
            {plan.originMission ? (
              <View style={styles.originBox}>
                <Text style={styles.originLabel}>Nasceu da missao</Text>
                <Text style={styles.originText}>{plan.originMission}</Text>
              </View>
            ) : null}
            <Text style={styles.detail}>{plan.time}</Text>
            <Text style={styles.detail}>{plan.place}</Text>
            <Text style={styles.accessibility}>{plan.accessibility}</Text>
            <View style={styles.notificationBox}>
              <Text style={styles.notificationTitle}>
                Aviso enviado ao circulo
              </Text>
              <Text style={styles.notificationText}>
                {seenCount}/{plan.capacity} viram ou responderam.{" "}
                {response?.detailsViews
                  ? `${response.detailsViews} pediu detalhes.`
                  : "Ainda sem pedidos de detalhes."}
              </Text>
            </View>
            <View style={styles.planFooter}>
              <View>
                <Text style={styles.deadline}>
                  {acceptedCount}/{plan.capacity} alinharam
                </Text>
                <Text style={styles.host}>Anfitriao: {plan.host}</Text>
              </View>
              <Text style={styles.deadline}>{plan.deadline}</Text>
            </View>
            {response?.notNowReason ? (
              <View style={styles.hostInsight}>
                <Text style={styles.hostInsightTitle}>Feedback ao anfitriao</Text>
                <Text style={styles.hostInsightText}>
                  1 pessoa respondeu: {response.notNowReason}.
                </Text>
                <Text style={styles.hostInsightText}>
                  {suggestionFor(response.notNowReason)}
                </Text>
              </View>
            ) : response?.detailsViews ? (
              <View style={styles.hostInsight}>
                <Text style={styles.hostInsightTitle}>Feedback ao anfitriao</Text>
                <Text style={styles.hostInsightText}>
                  Ha interesse, mas ainda falta confirmacao.
                </Text>
                <Text style={styles.hostInsightText}>
                  Sugestao: reforcar hora, ponto de encontro e custo para
                  reduzir duvida.
                </Text>
              </View>
            ) : null}
            {status === "checkedIn" ? (
              <View style={styles.doneBox}>
                <Text style={styles.doneTitle}>Presenca confirmada</Text>
                <Text style={styles.doneText}>
                  Depois do plano, a memoria aparece em Memorias.
                </Text>
              </View>
            ) : status === "accepted" ? (
              <View style={styles.actions}>
                <ActionButton
                  style={styles.actionGrow}
                  onPress={() => {
                    updateStatus(plan.id, "checkedIn");
                    onCheckIn(plan);
                  }}
                >
                  Fazer check-in
                </ActionButton>
                <ActionButton
                  variant="ghost"
                  style={styles.actionGrow}
                  onPress={() => updateStatus(plan.id, "open")}
                >
                  Afinal nao da
                </ActionButton>
              </View>
            ) : status === "dismissed" ? (
              <View style={styles.dismissedBox}>
                <Text style={styles.dismissedTitle}>Resposta guardada</Text>
                <Text style={styles.dismissedText}>
                  Sem culpa. O anfitriao recebe o sinal para melhorar o plano.
                </Text>
                <ActionButton
                  variant="secondary"
                  onPress={() => {
                    updateStatus(plan.id, "open");
                    setPlanResponses((current) => ({
                      ...current,
                      [plan.id]: {}
                    }));
                  }}
                >
                  Reconsiderar
                </ActionButton>
              </View>
            ) : (
              <View style={styles.actions}>
                <ActionButton
                  style={styles.actionGrow}
                  onPress={() => setSelectedPlan(plan)}
                >
                  Alinhar
                </ActionButton>
                <ActionButton
                  variant="secondary"
                  style={styles.actionGrow}
                  onPress={() => openDetails(plan)}
                >
                  Saber mais
                </ActionButton>
                <ActionButton
                  variant="ghost"
                  style={styles.actionGrow}
                  onPress={() => setNotNowPlan(plan)}
                >
                  Agora nao
                </ActionButton>
              </View>
            )}
          </View>
        );
      })}

      <Modal
        animationType="slide"
        transparent
        visible={selectedPlan !== null}
        onRequestClose={() => setSelectedPlan(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {selectedPlan ? (
              <>
                <Text style={styles.modalTitle}>{selectedPlan.title}</Text>
                <Text style={styles.modalText}>{selectedPlan.safetyNote}</Text>
                <View style={styles.checklist}>
                  {selectedPlan.checklist.map((item) => (
                    <View key={item} style={styles.checklistItem}>
                      <Text style={styles.check}>OK</Text>
                      <Text style={styles.checkText}>{item}</Text>
                    </View>
                  ))}
                </View>
                <ActionButton
                  onPress={() => {
                    updateStatus(selectedPlan.id, "accepted");
                    setSelectedPlan(null);
                  }}
                >
                  Confirmar que alinho
                </ActionButton>
                <ActionButton
                  variant="ghost"
                  onPress={() => setSelectedPlan(null)}
                >
                  Ver melhor depois
                </ActionButton>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={detailsPlan !== null}
        onRequestClose={() => setDetailsPlan(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {detailsPlan ? (
              <>
                <Text style={styles.modalKicker}>Saber mais</Text>
                <Text style={styles.modalTitle}>{detailsPlan.title}</Text>
                <Text style={styles.modalText}>{detailsPlan.safetyNote}</Text>
                {detailsPlan.originMission ? (
                  <View style={styles.originBox}>
                    <Text style={styles.originLabel}>Missao de origem</Text>
                    <Text style={styles.originText}>
                      {detailsPlan.originMission}
                    </Text>
                  </View>
                ) : null}
                <Text style={styles.modalDetail}>Quando: {detailsPlan.time}</Text>
                <Text style={styles.modalDetail}>Onde: {detailsPlan.place}</Text>
                <Text style={styles.modalDetail}>
                  Custo: {detailsPlan.costTier}
                </Text>
                <Text style={styles.modalDetail}>
                  Acessibilidade: {detailsPlan.accessibility}
                </Text>
                <ActionButton
                  onPress={() => {
                    updateStatus(detailsPlan.id, "accepted");
                    setPlanResponses((current) => ({
                      ...current,
                      [detailsPlan.id]: {
                        ...current[detailsPlan.id],
                        notNowReason: undefined
                      }
                    }));
                    setDetailsPlan(null);
                  }}
                >
                  Alinhar
                </ActionButton>
                <ActionButton
                  variant="secondary"
                  onPress={() => {
                    setNotNowPlan(detailsPlan);
                    setDetailsPlan(null);
                  }}
                >
                  Agora nao
                </ActionButton>
                <ActionButton variant="ghost" onPress={() => setDetailsPlan(null)}>
                  Fechar
                </ActionButton>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={notNowPlan !== null}
        onRequestClose={() => setNotNowPlan(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {notNowPlan ? (
              <>
                <Text style={styles.modalKicker}>Agora nao</Text>
                <Text style={styles.modalTitle}>O que tornava isto mais facil?</Text>
                <Text style={styles.modalText}>
                  A tua resposta ajuda o anfitriao a melhorar hora, dia, local,
                  preco ou energia do plano.
                </Text>
                {notNowReasons.map((reason) => (
                  <ActionButton
                    key={reason}
                    variant="secondary"
                    onPress={() => dismissPlan(notNowPlan.id, reason)}
                  >
                    {reason}
                  </ActionButton>
                ))}
                <ActionButton variant="ghost" onPress={() => setNotNowPlan(null)}>
                  Voltar
                </ActionButton>
              </>
            ) : null}
          </View>
        </View>
      </Modal>
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
    flexWrap: "wrap",
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
  originBox: {
    backgroundColor: colors.coralSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 4
  },
  originLabel: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  originText: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  deadline: {
    color: colors.blue,
    fontSize: 14,
    fontWeight: "800",
    letterSpacing: 0
  },
  host: {
    color: colors.inkMuted,
    fontSize: 13,
    marginTop: 3,
    letterSpacing: 0
  },
  planFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12
  },
  actions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10
  },
  actionGrow: {
    flexGrow: 1,
    minWidth: 120
  },
  doneBox: {
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 3
  },
  doneTitle: {
    color: colors.green,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  doneText: {
    color: colors.inkMuted,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  dismissedBox: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    padding: 12,
    gap: 9
  },
  dismissedTitle: {
    color: colors.ink,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  dismissedText: {
    color: colors.inkMuted,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  hostInsight: {
    backgroundColor: colors.goldSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 4
  },
  hostInsightTitle: {
    color: colors.gold,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  hostInsightText: {
    color: colors.ink,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  notificationBox: {
    backgroundColor: colors.blueSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 4
  },
  notificationTitle: {
    color: colors.blue,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  notificationText: {
    color: colors.ink,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  modalBackdrop: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(31, 39, 35, 0.42)"
  },
  modalCard: {
    backgroundColor: colors.background,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.lg,
    padding: 20,
    paddingBottom: 30,
    gap: 14
  },
  modalTitle: {
    color: colors.ink,
    fontSize: 26,
    lineHeight: 30,
    fontWeight: "900",
    letterSpacing: 0
  },
  modalKicker: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  modalText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  modalDetail: {
    color: colors.ink,
    fontSize: 15,
    lineHeight: 21,
    letterSpacing: 0
  },
  checklist: {
    gap: 10
  },
  checklistItem: {
    flexDirection: "row",
    gap: 9,
    alignItems: "flex-start"
  },
  check: {
    color: colors.green,
    fontSize: 15,
    fontWeight: "900",
    lineHeight: 20
  },
  checkText: {
    flex: 1,
    color: colors.ink,
    fontSize: 15,
    lineHeight: 20,
    letterSpacing: 0
  }
});
