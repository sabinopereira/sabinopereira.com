import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import {
  Image,
  Modal,
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

const energyLabel: Record<AppPreferences["usualEnergy"], string> = {
  baixa: "Energia baixa",
  media: "Energia media",
  alta: "Energia alta"
};

const socialComfortLabel: Record<AppPreferences["socialComfort"], string> = {
  sozinho: "Melhor sozinho/a",
  uma_pessoa: "Melhor com uma pessoa",
  grupo_pequeno: "Grupo pequeno",
  grupo: "Grupo"
};

const activityCompanyLabel: Record<
  AppPreferences["activityCompanyPreference"],
  string
> = {
  sozinho: "Atividades sozinho/a",
  uma_pessoa: "Atividades a dois",
  grupo_pequeno: "Atividades em grupo pequeno",
  grupo_aberto: "Atividades em grupo aberto",
  depende: "Depende da atividade"
};

const soloIdeasLabel: Record<AppPreferences["soloIdeasPreference"], string> = {
  sim: "Quer ideias individuais",
  as_vezes: "Ideias individuais as vezes",
  com_pessoas: "Prefere ideias com pessoas"
};

const authMethodLabel: Record<NonNullable<AppUser["authMethod"]>, string> = {
  email: "Email e password",
  apple: "Apple",
  google: "Google"
};

export function ProfileScreen({
  preferences,
  progress,
  user,
  onUserChange,
  onPreferencesChange,
  onLogout
}: {
  preferences: AppPreferences;
  progress: ProgressPath;
  user: AppUser;
  onUserChange: (user: AppUser) => void;
  onPreferencesChange: (preferences: AppPreferences) => void;
  onLogout: () => void;
}) {
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [publicProfileEditing, setPublicProfileEditing] = useState(false);
  const [publicProfileSaved, setPublicProfileSaved] = useState(false);
  const [draftName, setDraftName] = useState(user.name ?? "");
  const [draftEmail, setDraftEmail] = useState(user.email ?? "");
  const [draftPassword, setDraftPassword] = useState("");
  const [missionsPaused, setMissionsPaused] = useState(false);
  const [pauseOpen, setPauseOpen] = useState(false);
  const [securityOpen, setSecurityOpen] = useState(false);
  const [logoutOpen, setLogoutOpen] = useState(false);
  const [draftUsername, setDraftUsername] = useState(user.username ?? "@tu");
  const [draftLocality, setDraftLocality] = useState(
    user.locality ?? "A tua zona"
  );
  const visibility = user.visibility ?? {
    showPhoto: true,
    showName: true,
    showUsername: true,
    showLocality: true
  };
  const avatarInitial = (user.name || user.username || "Tu")
    .replace("@", "")
    .trim()
    .slice(0, 1)
    .toUpperCase();
  const rhythmChoices = [
    preferences.privateFirst ? "Comecar sozinho/a" : "Comecar com pessoas",
    `${preferences.maxMinutes} min maximo`,
    costLabel[preferences.preferredCostTier],
    intensityLabel[preferences.preferredIntensity],
    modeLabel[preferences.primaryMode],
    energyLabel[preferences.usualEnergy],
    socialComfortLabel[preferences.socialComfort],
    activityCompanyLabel[preferences.activityCompanyPreference],
    soloIdeasLabel[preferences.soloIdeasPreference],
    preferences.hasChildren ? "Tenho filhos" : null,
    preferences.hasPets ? "Tenho animais" : null,
    ...preferences.availability,
    ...preferences.likedActivities,
    ...preferences.accessibility
  ].filter(Boolean);
  const smartHelpOptions: Array<{
    key: keyof AppPreferences["smartHelp"];
    label: string;
    text: string;
  }> = [
    {
      key: "suggestMissions",
      label: "Sugerir missoes para mim",
      text: "Ajustar ideias ao teu ritmo, tempo e energia."
    },
    {
      key: "improveCreatedPlans",
      label: "Melhorar planos que eu crio",
      text: "Sugerir hora, local, custo e texto mais claro."
    },
    {
      key: "summarizeCircleFeedback",
      label: "Resumir feedback do circulo",
      text: "Juntar sinais como hora dificil, custo alto ou falta de detalhes."
    },
    {
      key: "useHistoryForRecommendations",
      label: "Usar historico para recomendacoes",
      text: "Aprender com o que aceitaste, adiaste ou completaste."
    },
    {
      key: "flagDiscomfortSignals",
      label: "Alertar sobre sinais de desconforto",
      text: "Mostrar avisos suaves quando houver sinais a rever."
    }
  ];

  function saveAccount() {
    onUserChange({
      ...user,
      entryType: "account",
      authMethod: "email",
      name: draftName.trim() || undefined,
      email: draftEmail.trim() || undefined,
      hasPassword: Boolean(draftPassword.trim()) || user.hasPassword
    });
    setDraftPassword("");
    setShowAccountForm(false);
  }

  function updateVisibility(nextVisibility: AppUser["visibility"]) {
    setPublicProfileSaved(false);
    onUserChange({
      ...user,
      visibility: nextVisibility
    });
  }

  async function choosePhoto() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permission.granted) {
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.75,
      mediaTypes: ["images"]
    });

    if (!result.canceled && result.assets[0]?.uri) {
      onUserChange({
        ...user,
        photoUri: result.assets[0].uri,
        visibility: {
          ...visibility,
          showPhoto: true
        }
      });
    }
  }

  function savePublicProfile() {
    onUserChange({
      ...user,
      username: draftUsername.trim() || "@tu",
      locality: draftLocality.trim() || "A tua zona",
      visibility
    });
    setPublicProfileEditing(false);
    setPublicProfileSaved(true);
  }

  function toggleSmartHelp(key: keyof AppPreferences["smartHelp"]) {
    onPreferencesChange({
      ...preferences,
      smartHelp: {
        ...preferences.smartHelp,
        [key]: !preferences.smartHelp[key]
      }
    });
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
        <View style={styles.photoRow}>
          <View style={styles.profilePhoto}>
            {user.photoUri ? (
              <Image source={{ uri: user.photoUri }} style={styles.photoImage} />
            ) : (
              <Text style={styles.photoInitial}>{avatarInitial || "T"}</Text>
            )}
          </View>
          <View style={styles.photoCopy}>
            <Text style={styles.photoTitle}>Foto de perfil</Text>
            <Text style={styles.photoText}>
              Pode aparecer em circulos e planos se escolheres mostrar.
            </Text>
          </View>
        </View>
        <View style={styles.photoActions}>
          <ActionButton
            variant="secondary"
            style={styles.photoAction}
            onPress={choosePhoto}
          >
            Alterar foto
          </ActionButton>
          <ActionButton
            variant="ghost"
            style={styles.photoAction}
            onPress={() =>
              onUserChange({
                ...user,
                photoUri: undefined
              })
            }
          >
            Usar iniciais
          </ActionButton>
        </View>
        <Text style={styles.accountTitle}>
          {user.entryType === "account"
            ? user.name || "Conta criada"
            : "A experimentar primeiro"}
        </Text>
        <Text style={styles.accountText}>
          {user.entryType === "account"
            ? `${authMethodLabel[user.authMethod ?? "email"]}${
                user.email ? ` - ${user.email}` : ""
              }${user.hasPassword ? " - password definida" : ""}`
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
            <TextInput
              value={draftUsername}
              onChangeText={setDraftUsername}
              placeholder="Username"
              placeholderTextColor={colors.inkMuted}
              autoCapitalize="none"
              style={styles.input}
            />
            <TextInput
              value={draftLocality}
              onChangeText={setDraftLocality}
              placeholder="Localidade"
              placeholderTextColor={colors.inkMuted}
              style={styles.input}
            />
            <TextInput
              value={draftPassword}
              onChangeText={setDraftPassword}
              placeholder={
                user.hasPassword ? "Nova password opcional" : "Password"
              }
              placeholderTextColor={colors.inkMuted}
              secureTextEntry
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
              setDraftPassword("");
              setShowAccountForm(true);
            }}
          >
            {user.entryType === "account" ? "Editar conta" : "Criar conta"}
          </ActionButton>
        )}
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>O que os outros veem</Text>
        <Text style={styles.text}>
          Dentro de circulos e planos, outras pessoas podem ver alguns dados
          para se sentirem mais seguras: nome, username e localidade aproximada.
          Tu escolhes o que aparece.
        </Text>
        <View style={styles.publicProfileBox}>
          <View style={styles.publicProfileRow}>
            {visibility.showPhoto ? (
              <View style={styles.publicPhoto}>
                {user.photoUri ? (
                  <Image
                    source={{ uri: user.photoUri }}
                    style={styles.publicPhotoImage}
                  />
                ) : (
                  <Text style={styles.publicPhotoInitial}>
                    {avatarInitial || "T"}
                  </Text>
                )}
              </View>
            ) : null}
            <View style={styles.publicCopy}>
              <Text style={styles.publicName}>
                {visibility.showName
                  ? user.name || "O teu nome"
                  : "Nome escondido"}
              </Text>
              <Text style={styles.publicMeta}>
                {visibility.showUsername ? user.username ?? "@tu" : "@escondido"}
                {" · "}
                {visibility.showLocality
                  ? user.locality ?? "A tua zona"
                  : "localidade escondida"}
              </Text>
            </View>
          </View>
        </View>
        {publicProfileSaved ? (
          <Text style={styles.publicSavedText}>Visibilidade guardada.</Text>
        ) : null}
        {publicProfileEditing ? (
          <>
            <View style={styles.toggleGrid}>
              <ActionButton
                variant={visibility.showPhoto ? "secondary" : "ghost"}
                style={styles.toggleButton}
                onPress={() =>
                  updateVisibility({
                    ...visibility,
                    showPhoto: !visibility.showPhoto
                  })
                }
              >
                Foto
              </ActionButton>
              <ActionButton
                variant={visibility.showName ? "secondary" : "ghost"}
                style={styles.toggleButton}
                onPress={() =>
                  updateVisibility({
                    ...visibility,
                    showName: !visibility.showName
                  })
                }
              >
                Nome
              </ActionButton>
              <ActionButton
                variant={visibility.showUsername ? "secondary" : "ghost"}
                style={styles.toggleButton}
                onPress={() =>
                  updateVisibility({
                    ...visibility,
                    showUsername: !visibility.showUsername
                  })
                }
              >
                Username
              </ActionButton>
              <ActionButton
                variant={visibility.showLocality ? "secondary" : "ghost"}
                style={styles.toggleButton}
                onPress={() =>
                  updateVisibility({
                    ...visibility,
                    showLocality: !visibility.showLocality
                  })
                }
              >
                Localidade
              </ActionButton>
            </View>
            <View style={styles.accountForm}>
              <TextInput
                value={draftUsername}
                onChangeText={setDraftUsername}
                placeholder="Username"
                placeholderTextColor={colors.inkMuted}
                autoCapitalize="none"
                style={styles.input}
              />
              <TextInput
                value={draftLocality}
                onChangeText={setDraftLocality}
                placeholder="Localidade aproximada"
                placeholderTextColor={colors.inkMuted}
                style={styles.input}
              />
              <ActionButton variant="secondary" onPress={savePublicProfile}>
                Guardar visibilidade
              </ActionButton>
            </View>
          </>
        ) : (
          <ActionButton
            variant="secondary"
            onPress={() => {
              setDraftUsername(user.username ?? "@tu");
              setDraftLocality(user.locality ?? "A tua zona");
              setPublicProfileSaved(false);
              setPublicProfileEditing(true);
            }}
          >
            Editar o que aparece
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
          {rhythmChoices.map((item, index) => (
            <Pill key={`${item}-${index}`} tone="blue">
              {item}
            </Pill>
          ))}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Ajuda inteligente</Text>
        <Text style={styles.text}>
          A app pode usar ajuda inteligente por tras para sugerir, resumir e
          melhorar planos. Tu decides o que fica ligado.
        </Text>
        <View style={styles.smartList}>
          {smartHelpOptions.map((option) => {
            const enabled = preferences.smartHelp[option.key];
            return (
              <View key={option.key} style={styles.smartItem}>
                <View style={styles.smartCopy}>
                  <Text style={styles.smartTitle}>{option.label}</Text>
                  <Text style={styles.smartText}>{option.text}</Text>
                </View>
                <ActionButton
                  variant={enabled ? "secondary" : "ghost"}
                  style={styles.smartButton}
                  onPress={() => toggleSmartHelp(option.key)}
                >
                  {enabled ? "Ligado" : "Desligado"}
                </ActionButton>
              </View>
            );
          })}
        </View>
      </View>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Hoje nao da</Text>
        <Text style={styles.text}>
          {missionsPaused
            ? "Missoes pausadas. A app nao deve insistir quando precisas de espaco."
            : "A app adapta as proximas missoes quando falta tempo, energia ou vontade."}
        </Text>
      </View>
      <ActionButton variant="secondary" onPress={() => setPauseOpen(true)}>
        {missionsPaused ? "Retomar missoes" : "Pausar missoes"}
      </ActionButton>
      <ActionButton variant="ghost" onPress={() => setSecurityOpen(true)}>
        Seguranca e bloqueios
      </ActionButton>
      <ActionButton variant="ghost" onPress={() => setLogoutOpen(true)}>
        Terminar sessao
      </ActionButton>

      <Modal
        animationType="slide"
        transparent
        visible={pauseOpen}
        onRequestClose={() => setPauseOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalKicker}>Ritmo</Text>
            <Text style={styles.modalTitle}>
              {missionsPaused ? "Retomar missoes?" : "Pausar missoes?"}
            </Text>
            <Text style={styles.modalText}>
              {missionsPaused
                ? "Voltamos a mostrar sugestoes no Hoje."
                : "A pausa reduz pressao. Podes voltar quando fizer sentido."}
            </Text>
            <ActionButton
              onPress={() => {
                setMissionsPaused(!missionsPaused);
                setPauseOpen(false);
              }}
            >
              {missionsPaused ? "Retomar" : "Pausar"}
            </ActionButton>
            <ActionButton variant="ghost" onPress={() => setPauseOpen(false)}>
              Voltar
            </ActionButton>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={securityOpen}
        onRequestClose={() => setSecurityOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalKicker}>Seguranca</Text>
            <Text style={styles.modalTitle}>Controlos de seguranca</Text>
            <Text style={styles.modalText}>
              Podes reduzir convites nos circulos, esconder planos e enviar
              sinais de seguranca. Esses controlos aparecem em Circulos e
              Alinhar.
            </Text>
            <View style={styles.securityList}>
              <Text style={styles.securityItem}>OK Nome, foto e localidade controlados por ti.</Text>
              <Text style={styles.securityItem}>OK Sinais de seguranca sao privados.</Text>
              <Text style={styles.securityItem}>OK Planos podem ser escondidos.</Text>
            </View>
            <ActionButton onPress={() => setSecurityOpen(false)}>
              Entendi
            </ActionButton>
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={logoutOpen}
        onRequestClose={() => setLogoutOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <Text style={styles.modalKicker}>Conta</Text>
            <Text style={styles.modalTitle}>Terminar sessao?</Text>
            <Text style={styles.modalText}>
              Vais voltar ao inicio da app. As tuas escolhas e memorias neste
              telemovel ficam guardadas.
            </Text>
            <ActionButton
              onPress={() => {
                setLogoutOpen(false);
                onLogout();
              }}
            >
              Terminar sessao
            </ActionButton>
            <ActionButton variant="ghost" onPress={() => setLogoutOpen(false)}>
              Cancelar
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
  photoRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12
  },
  profilePhoto: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.green,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden"
  },
  photoImage: {
    width: 72,
    height: 72
  },
  photoInitial: {
    color: "#FFFFFF",
    fontSize: 28,
    fontWeight: "900",
    letterSpacing: 0
  },
  photoCopy: {
    flex: 1,
    gap: 3
  },
  photoTitle: {
    color: colors.ink,
    fontSize: 16,
    fontWeight: "900",
    letterSpacing: 0
  },
  photoText: {
    color: colors.inkMuted,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  photoActions: {
    flexDirection: "row",
    gap: 8
  },
  photoAction: {
    flex: 1
  },
  publicProfileBox: {
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 3
  },
  publicProfileRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10
  },
  publicPhoto: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: colors.green,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden"
  },
  publicPhotoImage: {
    width: 42,
    height: 42
  },
  publicPhotoInitial: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "900",
    letterSpacing: 0
  },
  publicCopy: {
    flex: 1,
    gap: 2
  },
  publicName: {
    color: colors.ink,
    fontSize: 17,
    fontWeight: "900",
    letterSpacing: 0
  },
  publicMeta: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 19,
    letterSpacing: 0
  },
  publicSavedText: {
    color: colors.green,
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "800",
    letterSpacing: 0
  },
  toggleGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8
  },
  toggleButton: {
    flexGrow: 1
  },
  smartList: {
    gap: 10
  },
  smartItem: {
    backgroundColor: colors.surfaceMuted,
    borderRadius: radius.sm,
    padding: 12,
    gap: 10
  },
  smartCopy: {
    gap: 3
  },
  smartTitle: {
    color: colors.ink,
    fontSize: 15,
    fontWeight: "900",
    letterSpacing: 0
  },
  smartText: {
    color: colors.inkMuted,
    fontSize: 13,
    lineHeight: 18,
    letterSpacing: 0
  },
  smartButton: {
    alignSelf: "flex-start",
    minWidth: 116
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
  securityList: {
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 7
  },
  securityItem: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "700",
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
