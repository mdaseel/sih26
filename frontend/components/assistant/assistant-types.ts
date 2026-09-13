export type AssistantRole = "CITIZEN" | "DISCOM" | "VENDOR" | "ADMIN";

export interface AssistantContext {
  page?: string;
  application_id?: string | null;
  pv_bus?: string | null;
  selected_asset_id?: string | null;
  selected_asset_type?: string | null;
  assessment_id?: string | null;
}

export interface AssistantMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  actions?: AssistantAction[];
  timestamp: string;
}

export type SolarGridAssistantAction =
  | { type: "FOCUS_BUS"; payload: { busId: string } }
  | { type: "FOCUS_TRANSFORMER"; payload: { transformerId: string } }
  | { type: "FOCUS_LINE"; payload: { lineId: string } }
  | { type: "FOCUS_HOUSE"; payload: { houseId: string } }
  | { type: "FOCUS_APPLICATION"; payload: { applicationId: string } }
  | { type: "HIGHLIGHT_PATH"; payload: { assetIds: string[] } }
  | { type: "OPEN_ASSESSMENT"; payload: { assessmentId: string } }
  | { type: "SHOW_ASSESSMENT_LOCATION"; payload: { pv_bus: string } };

export type AssistantAction = SolarGridAssistantAction;

export interface AssistantSuggestion {
  label: string;
  prompt: string;
}
