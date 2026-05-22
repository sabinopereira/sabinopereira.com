import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View
} from "react-native";

import { ActionButton } from "../components/ActionButton";
import { Pill } from "../components/Pill";
import { AppPreferences } from "../data/preferences";
import { ProgressPath } from "../data/progress";
import { AppUser } from "../data/user";
import { colors, radius } from "../theme/colors";

const modeLabel: Record<AppPreferences["primaryMode"], string> = {
  coragem: "Aventura",
  social: "Social",
  familia: "Familia",
  saude: "Saude",
  recomeco: "Recuperar ritmo"
};

const costLabel: Record<AppPreferences["preferredCostTier"], string> = {
  gratis: "Gratis",
  low_cost: "Low cost",
  medio: "Medio",
  especial: "Especial"
};

const intensityLabel: Record<AppPreferences["preferredIntensity"], string> = {
  leve: "Leve",
  real: "Real",
  coragem: "Aventura"
};

export function ProfileScreen({
  preferences,
  progress,
  user,
  onUserChange
}: {
  preferences: AppPreferences;
  progress: ProgressPath;
  user: AppUser;
  onUserChange: (user: AppUser) => void;
}) {
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [draftName, setDraftName] = useState(user.name ?? "");
  const [draftEmail, setDraftEmail] = useState(user.email ?? "");
  const rhythmChoices = [
    preferences.privateFirst ? "Comecar sozinho/a" : "Comecar com pessoas",
    `${preferences.maxMinutes} min maximo`,
    costLabel[preferences.preferredCostTier],
    intensityLabel[preferences.preferredIntensity],
    modeLabel[preferences.primaryMode],
    preferences.hasChildren ? "Tenho filhos" : null,
    ...preferences.accessibility
  ].filter(Boolean);

  function saveAccount() {
    onUserChange({
      entryType: "account",
      name: draftName.trim() || undefined,
      email: draftEmail.trim() || undefined
    });
    setShowAccountForm(false);
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Perfil</Text>
        <Text style={styles.subtitle}>
          O teu ritmo, as tuas escolhas e a tua seguranca.
        </Text>
      </View>
      <View style={styles.accountCard}>
        <Text style={styles.accountKicker}>Conta</Text>
        <Text style={styles.accountTitle}>
          {user.entryType === "account"
            ? user.name || "Conta criada"
            : "A experimentar primeiro"}
        </Text>
        <Text style={styles.accountText}>
          {user.entryType === "account"
            ? user.email || "Os teus dados ficam guardados neste telemovel."
            : "Podes usar a app ja. Quando quiseres, crias conta para associar o caminho ao teu email."}
        </Text>
        {showAccountForm ? (
          <View style={styles.accountForm}>
            <TextInput
              value={draftName}
              onChangeText={setDraftName}
              placeholder="Nome"
              placeholderTextColor={colors.inkMuted}
              style={styles.input}
            />
            <TextInput
              value={draftEmail}
              onChangeText={setDraftEmail}
              placeholder="Email"
              placeholderTextColor={colors.inkMuted}
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
            />
            <ActionButton onPress={saveAccount}>Guardar conta</ActionButton>
          </View>
        ) : (
          <ActionButton
            variant="secondary"
            onPress={() => {
              setDraftName(user.name ?? "");
              setDraftEmail(user.email ?? "");
              setShowAccountForm(true);
            }}
          >
            {user.entryType === "account" ? "Editar conta" : "Criar conta"}
          </ActionButton>
        )}
      </View>
      <View style={styles.pathCard}>
        <Text style={styles.pathKicker}>O teu caminho</Text>
        <Text style={styles.pathTitle}>{progress.currentStage}</Text>
        <Text style={styles.pathText}>{progress.label}</Text>
        <View style={styles.progressTrack}>
          <View
            style={[
              styles.progressFill,
              { width: `${Math.round(progress.progressRatio * 100)}%` }
            ]}
          />
        </View>
        <Text style={styles.pathHint}>
          {progress.nextStage && progress.nextTarget
            ? `Proximo: ${progress.nextStage} aos ${progress.nextTarget} momentos.`
            : "Caminho aberto. Agora podes ajudar outros a entrar."}
        </Text>
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.missionCount}</Text>
            <Text style={styles.statLabel}>missoes</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.planCount}</Text>
            <Text style={styles.statLabel}>planos</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{progress.completedCount}</Text>
            <Text style={styles.statLabel}>momentos</Text>
          </View>
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Marcos</Text>
        <View style={styles.milestones}>
          {progress.milestones.map((milestone) => (
            <View key={milestone.label} style={styles.milestone}>
              <Text
                style={[
                  styles.milestoneMark,
                  !milestone.unlocked && styles.milestoneLocked
                ]}
              >
                {milestone.unlocked ? "OK" : "--"}
              </Text>
              <Text
                style={[
                  styles.milestoneText,
                  !milestone.unlocked && styles.milestoneLocked
                ]}
              >
                {milestone.label}
              </Text>
            </View>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O que queres mexer</Text>
        <View style={styles.pills}>
          {preferences.routineFocus.map((item) => (
            <Pill key={item} tone="green">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O teu ritmo</Text>
        <View style={styles.pills}>
          {rhythmChoices.map((item) => (
            <Pill key={item} tone="blue">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Hoje nao da</Text>
        <Text style={styles.text}>
          A app adapta as proximas missoes quando falta tempo, energia ou
          vontade.
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
  accountCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 18,
    gap: 7,
    borderWidth: 1,
    borderColor: colors.line
  },
  accountKicker: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  accountTitle: {
    color: colors.ink,
    fontSize: 22,
    lineHeight: 26,
    fontWeight: "900",
    letterSpacing: 0
  },
  accountText: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  accountForm: {
    gap: 8
  },
  input: {
    minHeight: 46,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    color: colors.ink,
    paddingHorizontal: 13,
    fontSize: 15,
    letterSpacing: 0
  },
  pathCard: {
    backgroundColor: colors.green,
    borderRadius: radius.lg,
    padding: 18,
    gap: 12
  },
  pathKicker: {
    color: colors.greenSoft,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  pathTitle: {
    color: "#FFFFFF",
    fontSize: 30,
    lineHeight: 34,
    fontWeight: "900",
    letterSpacing: 0
  },
  pathText: {
    color: "#EEF6EF",
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
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
  pathHint: {
    color: "#EEF6EF",
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  statsRow: {
    flexDirection: "row",
    gap: 10
  },
  statBox: {
    flex: 1,
    backgroundColor: "rgba(255, 255, 255, 0.12)",
    borderRadius: radius.sm,
    padding: 10,
    gap: 2
  },
  statNumber: {
    color: "#FFFFFF",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0,
    fontVariant: ["tabular-nums"]
  },
  statLabel: {
    color: colors.greenSoft,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0
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
  milestones: {
    gap: 10
  },
  milestone: {
    flexDirection: "row",
    gap: 10,
    alignItems: "center"
  },
  milestoneMark: {
    color: colors.green,
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    overflow: "hidden",
    paddingHorizontal: 8,
    paddingVertical: 4,
    fontSize: 12,
    fontWeight: "900",
    letterSpacing: 0
  },
  milestoneText: {
    flex: 1,
    color: colors.ink,
    fontSize: 15,
    lineHeight: 20,
    fontWeight: "700",
    letterSpacing: 0
  },
  milestoneLocked: {
    color: colors.inkMuted
  },
  text: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
