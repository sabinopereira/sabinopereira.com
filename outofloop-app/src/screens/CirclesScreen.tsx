import { useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { circles, UpcomingPlan } from "../data/mockMissions";
import { colors, radius } from "../theme/colors";

type Circle = (typeof circles)[number];

const planTemplates = [
  {
    title: "Cafe curto sem complicar",
    originMission: "Convida alguem para um encontro simples.",
    time: "Hoje, 18:30",
    place: "Cafe perto de todos",
    durationLabel: "leve",
    accessibility: "baixo custo, facil de sair cedo",
    checklist: [
      "Confirmar quem vem",
      "Escolher sitio simples",
      "Nao transformar isto num grande evento"
    ]
  },
  {
    title: "Volta curta para respirar",
    originMission: "Sai da rotina com uma caminhada leve.",
    time: "Amanha, fim de tarde",
    place: "Jardim ou rua calma",
    durationLabel: "realista",
    accessibility: "percurso curto, ritmo calmo",
    checklist: [
      "Combinar ponto de encontro",
      "Avisar se precisares de banco ou pausa",
      "Ir mesmo que sejam so duas pessoas"
    ]
  },
  {
    title: "Conversa a mesa",
    originMission: "Cria uma conversa real em familia ou circulo.",
    time: "Proximo jantar",
    place: "Casa",
    durationLabel: "realista",
    accessibility: "sentado, privado, previsivel",
    checklist: [
      "Escolher uma pergunta",
      "Cada pessoa pode passar",
      "Guardar uma memoria no fim"
    ]
  }
];

export function CirclesScreen({
  onCreatePlan
}: {
  onCreatePlan: (plan: UpcomingPlan) => void;
}) {
  const [selectedCircle, setSelectedCircle] = useState<Circle | null>(null);

  function createPlan(circle: Circle, template: (typeof planTemplates)[number]) {
    onCreatePlan({
      id: `plan-${circle.id}-${Date.now()}`,
      title: template.title,
      circle: circle.name,
      time: template.time,
      place: template.place,
      costTier: "gratis",
      durationLabel: template.durationLabel,
      acceptedCount: 1,
      capacity: circle.type === "Familia" ? 5 : 6,
      deadline: "fecha hoje as 21:00",
      accessibility: template.accessibility,
      host: "Tu",
      originMission: template.originMission,
      safetyNote:
        "Plano criado no circulo: hora, local, custo e conforto ficam claros antes de alguem responder.",
      checklist: template.checklist
    });
    setSelectedCircle(null);
  }

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
            <ActionButton
              variant="secondary"
              style={styles.actionGrow}
              onPress={() => setSelectedCircle(circle)}
            >
              Criar plano
            </ActionButton>
            <ActionButton variant="ghost" style={styles.actionGrow}>
              Convidar
            </ActionButton>
          </View>
        </View>
      ))}

      <ActionButton>Criar circulo</ActionButton>
      <ActionButton variant="ghost">Saltar grupos por agora</ActionButton>

      <Modal
        animationType="slide"
        transparent
        visible={selectedCircle !== null}
        onRequestClose={() => setSelectedCircle(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {selectedCircle ? (
              <>
                <Text style={styles.modalKicker}>Criar plano simples</Text>
                <Text style={styles.modalTitle}>{selectedCircle.name}</Text>
                <Text style={styles.modalText}>
                  Escolhe um plano simples. Ele aparece em Quem alinha? com
                  hora, local, custo e prazo para responder.
                </Text>
                {planTemplates.map((template) => (
                  <ActionButton
                    key={template.title}
                    variant="secondary"
                    onPress={() => createPlan(selectedCircle, template)}
                  >
                    {template.title}
                  </ActionButton>
                ))}
                <ActionButton
                  variant="ghost"
                  onPress={() => setSelectedCircle(null)}
                >
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
    gap: 12
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
    fontSize: 28,
    lineHeight: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  modalText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
