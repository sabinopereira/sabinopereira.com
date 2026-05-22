import { MaterialCommunityIcons } from "@expo/vector-icons";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import type { TabKey } from "../../App";
import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { SmartHint } from "../components/SmartHint";
import { UpcomingPlan } from "../data/mockMissions";
import { NotificationPreference } from "../data/notifications";
import { AppPreferences } from "../data/preferences";
import {
  PlanResponses,
  PlanStatus,
  PlanStatuses
} from "../data/planState";
import { colors, radius } from "../theme/colors";

function statusFor(planStatuses: PlanStatuses, planId: string): PlanStatus {
  return planStatuses[planId] ?? "open";
}

function suggestionFor(reason?: string) {
  switch (reason) {
    case "Hora dificil":
      return "Tenta sugerir duas horas alternativas.";
    case "Dia nao ajuda":
      return "Tenta outro dia ou passa para o fim de semana.";
    case "Fica longe":
      return "Escolhe um sitio mais central ou perto de transportes.";
    case "Custo alto":
      return "Troca por uma opcao gratis ou low cost.";
    case "Sem energia":
    case "Prefiro algo mais leve":
      return "Faz mais curto e deixa claro que sair cedo e ok.";
    default:
      return "Repete hora, local e custo para ajudar a decidir.";
  }
}

export function alertCountForPlans(
  plans: UpcomingPlan[],
  planStatuses: PlanStatuses,
  planResponses: PlanResponses
) {
  return plans.filter((plan) => {
    const status = statusFor(planStatuses, plan.id);
    const response = planResponses[plan.id];
    return (
      status === "open" ||
      status === "accepted" ||
      Boolean(response?.detailsViews || response?.notNowReason)
    );
  }).length;
}

export function AlertsScreen({
  plans,
  preferences,
  planStatuses,
  planResponses,
  onPlanStatusChange,
  onPlanResponseChange,
  onNavigate,
  notificationPreference,
  onEnableNotifications,
  onSendPlanReminder
}: {
  plans: UpcomingPlan[];
  preferences: AppPreferences;
  planStatuses: PlanStatuses;
  planResponses: PlanResponses;
  onPlanStatusChange: (planId: string, status: PlanStatus) => void;
  onPlanResponseChange: (planId: string, response: PlanResponses[string]) => void;
  onNavigate: (tab: TabKey) => void;
  notificationPreference: NotificationPreference;
  onEnableNotifications: () => void;
  onSendPlanReminder: (plan: UpcomingPlan) => void;
}) {
  const actionablePlans = plans.filter((plan) => {
    const status = statusFor(planStatuses, plan.id);
    const response = planResponses[plan.id];
    return (
      status === "open" ||
      status === "accepted" ||
      Boolean(response?.detailsViews || response?.notNowReason)
    );
  });

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Avisos</Text>
        <Text style={styles.subtitle}>
          Convites, respostas e sinais importantes dos teus circulos.
        </Text>
      </View>

      <View style={styles.notificationCard}>
        <View style={styles.notificationHeader}>
          <MaterialCommunityIcons
            name={
              notificationPreference === "enabled"
                ? "bell-check-outline"
                : "bell-ring-outline"
            }
            size={25}
            color={colors.green}
          />
          <View style={styles.notificationCopy}>
            <Text style={styles.notificationTitle}>Notificacoes</Text>
            <Text style={styles.notificationText}>
              {notificationPreference === "enabled"
                ? "Ativas neste telemovel."
                : notificationPreference === "disabled"
                  ? "Estao desligadas neste telemovel."
                  : "Liga para receber avisos importantes dos planos."}
            </Text>
          </View>
        </View>
        {notificationPreference === "enabled" ? null : (
          <ActionButton variant="secondary" onPress={onEnableNotifications}>
            Ligar notificacoes
          </ActionButton>
        )}
      </View>

      {actionablePlans.length === 0 ? (
        <View style={styles.emptyCard}>
          <MaterialCommunityIcons
            name="bell-check-outline"
            size={32}
            color={colors.green}
          />
          <Text style={styles.emptyTitle}>Tudo visto.</Text>
          <Text style={styles.emptyText}>
            Quando houver convites ou respostas novas, aparecem aqui.
          </Text>
        </View>
      ) : null}

      {actionablePlans.map((plan) => {
        const status = statusFor(planStatuses, plan.id);
        const response = planResponses[plan.id];
        const hasCreatorFeedback = Boolean(
          response?.detailsViews || response?.notNowReason
        );

        return (
          <View key={plan.id} style={styles.card}>
            <View style={styles.row}>
              <Pill tone="green">{plan.circle}</Pill>
              <Pill tone={status === "open" ? "coral" : "blue"}>
                {status === "accepted" ? "vais alinhar" : "resposta pedida"}
              </Pill>
            </View>
            <Text style={styles.cardTitle}>{plan.title}</Text>
            <Text style={styles.text}>{plan.time}</Text>
            <Text style={styles.text}>{plan.place}</Text>

            {status === "open" ? (
              <View style={styles.noticeBox}>
                <Text style={styles.noticeTitle}>Convite para plano</Text>
                <Text style={styles.noticeText}>
                  Responde quando souberes. Ajuda quem criou a perceber se o
                  plano faz sentido.
                </Text>
              </View>
            ) : null}

            {status === "accepted" ? (
              <View style={styles.noticeBox}>
                <Text style={styles.noticeTitle}>Falta o check-in</Text>
                <Text style={styles.noticeText}>
                  Depois do plano, confirma a presenca para guardar a memoria.
                </Text>
              </View>
            ) : null}

            {hasCreatorFeedback ? (
              <View style={styles.feedbackBox}>
                <Text style={styles.feedbackTitle}>Sinal para quem criou</Text>
                <Text style={styles.feedbackText}>
                  {response?.notNowReason
                    ? `1 pessoa respondeu: ${response.notNowReason}.`
                    : `${response?.detailsViews ?? 0} pediu detalhes.`}
                </Text>
                <Text style={styles.feedbackText}>
                  {suggestionFor(response?.notNowReason)}
                </Text>
              </View>
            ) : null}

            {hasCreatorFeedback &&
            preferences.smartHelp.summarizeCircleFeedback ? (
              <SmartHint
                title="Resumo inteligente"
                text={
                  response?.notNowReason
                    ? suggestionFor(response.notNowReason)
                    : "Ha interesse, mas ainda falta clareza. Reforca hora, local e custo."
                }
              />
            ) : null}

            <View style={styles.actions}>
              {status === "open" ? (
                <>
                  <ActionButton
                    style={styles.actionGrow}
                    onPress={() => onPlanStatusChange(plan.id, "accepted")}
                  >
                    Alinhar
                  </ActionButton>
                  <ActionButton
                    variant="secondary"
                    style={styles.actionGrow}
                    onPress={() => {
                      onPlanResponseChange(plan.id, {
                        ...response,
                        detailsViews: (response?.detailsViews ?? 0) + 1
                      });
                      onNavigate("align");
                    }}
                  >
                    Saber mais
                  </ActionButton>
                </>
              ) : (
                <ActionButton
                  style={styles.actionGrow}
                  onPress={() => onNavigate("align")}
                >
                  Ver plano
                </ActionButton>
              )}
              <ActionButton
                variant="ghost"
                style={styles.actionGrow}
                onPress={() => onNavigate("align")}
              >
                Abrir Alinhar
              </ActionButton>
              {notificationPreference === "enabled" ? (
                <ActionButton
                  variant="secondary"
                  style={styles.actionGrow}
                  onPress={() => onSendPlanReminder(plan)}
                >
                  Avisar-me
                </ActionButton>
              ) : null}
            </View>
          </View>
        );
      })}
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
  emptyCard: {
    backgroundColor: colors.greenSoft,
    borderRadius: radius.lg,
    padding: 20,
    gap: 10,
    borderWidth: 1,
    borderColor: colors.line
  },
  notificationCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 16,
    gap: 12,
    borderWidth: 1,
    borderColor: colors.line
  },
  notificationHeader: {
    flexDirection: "row",
    gap: 11,
    alignItems: "center"
  },
  notificationCopy: {
    flex: 1,
    gap: 3
  },
  notificationTitle: {
    color: colors.ink,
    fontSize: 16,
    fontWeight: "900",
    letterSpacing: 0
  },
  notificationText: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  emptyTitle: {
    color: colors.ink,
    fontSize: 22,
    lineHeight: 26,
    fontWeight: "900",
    letterSpacing: 0
  },
  emptyText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 22,
    lineHeight: 27,
    fontWeight: "900",
    letterSpacing: 0
  },
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 21,
    letterSpacing: 0
  },
  noticeBox: {
    backgroundColor: colors.blueSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 5
  },
  noticeTitle: {
    color: colors.blue,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  noticeText: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  feedbackBox: {
    backgroundColor: colors.goldSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 5
  },
  feedbackTitle: {
    color: colors.gold,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  feedbackText: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  actions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  actionGrow: {
    flexGrow: 1
  }
});
