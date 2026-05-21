import { useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { upcomingPlans } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

type PlanStatus = "open" | "accepted" | "checkedIn";
type Plan = (typeof upcomingPlans)[number];

export function AlignScreen({
  onCheckIn
}: {
  onCheckIn: (plan: Plan) => void;
}) {
  const [planStatuses, setPlanStatuses] = useState<Record<string, PlanStatus>>(
    {}
  );
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);

  function statusFor(planId: string): PlanStatus {
    return planStatuses[planId] ?? "open";
  }

  function updateStatus(planId: string, status: PlanStatus) {
    setPlanStatuses((current) => ({
      ...current,
      [planId]: status
    }));
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

      {upcomingPlans.map((plan) => {
        const status = statusFor(plan.id);
        const acceptedCount =
          status === "open" ? plan.acceptedCount : plan.acceptedCount + 1;
        const statusLabel =
          status === "checkedIn"
            ? "check-in feito"
            : status === "accepted"
              ? "alinhado"
              : "aberto";

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
            <Text style={styles.detail}>{plan.time}</Text>
            <Text style={styles.detail}>{plan.place}</Text>
            <Text style={styles.accessibility}>{plan.accessibility}</Text>
            <View style={styles.planFooter}>
              <View>
                <Text style={styles.deadline}>
                  {acceptedCount}/{plan.capacity} alinharam
                </Text>
                <Text style={styles.host}>Anfitriao: {plan.host}</Text>
              </View>
              <Text style={styles.deadline}>{plan.deadline}</Text>
            </View>
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
            ) : (
              <ActionButton onPress={() => setSelectedPlan(plan)}>
                Alinhar
              </ActionButton>
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
    gap: 10
  },
  actionGrow: {
    flex: 1
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
  modalText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
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
