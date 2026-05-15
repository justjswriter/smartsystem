import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, Hash, MapPin, Pencil, Plus, Trash2 } from "lucide-react";
import { getPlantCareProfiles, getPlantDashboard } from "../api";
import { CustomSelect } from "../components/CustomSelect";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import {
  displayPlantSpecies,
  SUPPORTED_PLANT_OPTIONS,
  SUPPORTED_PLANT_SPECIES,
  supportedPlantTypeName,
} from "../plantKnowledge";
import type { CareProfile, PlantCondition } from "../types";

export function PlantsIndexPage() {
  const { token, plants, isPlantsLoading, createPlantEntry, deletePlantEntry, renamePlantEntry } = useAppState();
  const { t, label, language } = useI18n();
  const [conditionByPlant, setConditionByPlant] = useState<Record<number, PlantCondition | null | undefined>>({});
  const [careProfiles, setCareProfiles] = useState<CareProfile[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [species, setSpecies] = useState(SUPPORTED_PLANT_SPECIES);
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [plantToDelete, setPlantToDelete] = useState<{ id: number; name: string } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [plantToRename, setPlantToRename] = useState<{ id: number; name: string } | null>(null);
  const [renameDraft, setRenameDraft] = useState("");
  const [isRenaming, setIsRenaming] = useState(false);
  const speciesOptions =
    careProfiles.length > 0
      ? careProfiles.map((profile) => profile.canonical_species)
      : [...SUPPORTED_PLANT_OPTIONS];

  useEffect(() => {
    if (!token || plants.length === 0) {
      setConditionByPlant({});
      return;
    }

    let cancelled = false;
    void Promise.all(
      plants.map(async (plant) => {
        try {
          const dashboard = await getPlantDashboard(token, plant.id, 24);
          return { id: plant.id, condition: dashboard.condition };
        } catch {
          return { id: plant.id, condition: null };
        }
      })
    ).then((rows) => {
      if (cancelled) {
        return;
      }
      const next: Record<number, PlantCondition | null> = {};
      for (const row of rows) {
        next[row.id] = row.condition;
      }
      setConditionByPlant(next);
    });

    return () => {
      cancelled = true;
    };
  }, [token, plants]);

  useEffect(() => {
    if (!token) {
      setCareProfiles([]);
      return;
    }

    let cancelled = false;
    void getPlantCareProfiles(token)
      .then((profiles) => {
        if (!cancelled) {
          setCareProfiles(profiles);
          if (profiles[0]?.canonical_species) {
            setSpecies(profiles[0].canonical_species);
          }
        }
      })
      .catch(() => {
        if (!cancelled) {
          setCareProfiles([]);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  function speciesLabel(option: string) {
    const profile = careProfiles.find((item) => item.canonical_species === option);
    return profile?.display_names?.[language] ?? displayPlantSpecies(option, t);
  }

  async function submitPlant(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await createPlantEntry({
        name: name.trim(),
        species,
        location: location.trim() || undefined,
        description: description.trim() || undefined,
      });
      setModalOpen(false);
      setName("");
      setSpecies(speciesOptions[0] ?? SUPPORTED_PLANT_SPECIES);
      setLocation("");
      setDescription("");
    } finally {
      setSaving(false);
    }
  }

  async function confirmDeletePlant() {
    if (!plantToDelete) {
      return;
    }
    setIsDeleting(true);
    try {
      await deletePlantEntry(plantToDelete.id);
      setPlantToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  }

  function openRenameDialog(plant: { id: number; name: string }) {
    setPlantToRename(plant);
    setRenameDraft(plant.name);
  }

  async function submitRenamePlant(event: React.FormEvent) {
    event.preventDefault();
    if (!plantToRename || !renameDraft.trim()) {
      return;
    }
    setIsRenaming(true);
    try {
      await renamePlantEntry(plantToRename.id, renameDraft.trim());
      setPlantToRename(null);
      setRenameDraft("");
    } finally {
      setIsRenaming(false);
    }
  }

  if (isPlantsLoading) {
    return <p className="muted page-lead">{t("plants.loading")}</p>;
  }

  const addPlantModal = modalOpen ? (
    <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="add-plant-title">
      <button type="button" className="modal-backdrop" aria-label={t("common.close")} onClick={() => setModalOpen(false)} />
      <div className="modal-panel card">
        <h2 id="add-plant-title">{t("dashboard.addPlantTitle")}</h2>
        <form className="modal-form" onSubmit={submitPlant}>
          <label>{t("dashboard.name")}<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
          <label>
            {t("dashboard.species")}
            <CustomSelect
              value={species}
              onChange={setSpecies}
              options={speciesOptions.map((option) => ({ value: option, label: speciesLabel(option) }))}
            />
          </label>
          <p className="muted small">{supportedPlantTypeName(t)}</p>
          <label>{t("dashboard.location")}<input value={location} onChange={(e) => setLocation(e.target.value)} /></label>
          <label>{t("dashboard.description")}<input value={description} onChange={(e) => setDescription(e.target.value)} /></label>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t("common.cancel")}</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? t("common.saving") : t("common.create")}</button>
          </div>
        </form>
      </div>
    </div>
  ) : null;
  const deletePlantModal = plantToDelete ? (
    <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="delete-plant-title">
      <button type="button" className="modal-backdrop" aria-label={t("common.close")} onClick={() => setPlantToDelete(null)} />
      <div className="modal-panel card confirm-dialog">
        <h2 id="delete-plant-title">{t("plants.deleteConfirmTitle")}</h2>
        <p className="muted">{t("plants.deleteConfirmText", { name: plantToDelete.name })}</p>
        <div className="modal-actions">
          <button type="button" className="btn-secondary" onClick={() => setPlantToDelete(null)} disabled={isDeleting}>
            {t("common.cancel")}
          </button>
          <button type="button" className="btn-danger" onClick={() => void confirmDeletePlant()} disabled={isDeleting}>
            {isDeleting ? t("common.saving") : t("plants.deleteConfirmYes")}
          </button>
        </div>
      </div>
    </div>
  ) : null;
  const renamePlantModal = plantToRename ? (
    <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="rename-plant-title">
      <button type="button" className="modal-backdrop" aria-label={t("common.close")} onClick={() => setPlantToRename(null)} />
      <div className="modal-panel card confirm-dialog">
        <h2 id="rename-plant-title">{t("plants.renameTitle")}</h2>
        <form className="modal-form" onSubmit={submitRenamePlant}>
          <label>
            {t("dashboard.name")}
            <input value={renameDraft} onChange={(event) => setRenameDraft(event.target.value)} required />
          </label>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setPlantToRename(null)} disabled={isRenaming}>
              {t("common.cancel")}
            </button>
            <button type="submit" className="btn-primary" disabled={isRenaming || !renameDraft.trim()}>
              {isRenaming ? t("common.saving") : t("common.save")}
            </button>
          </div>
        </form>
      </div>
    </div>
  ) : null;

  if (plants.length === 0) {
    return (
      <div className="page-stack">
        <div className="page-head">
          <div>
            <h1 className="page-title">{t("plants.title")}</h1>
            <p className="muted page-lead">{t("plants.empty")}</p>
          </div>
          <button type="button" className="btn-primary" onClick={() => setModalOpen(true)}>
            <Plus size={18} />
            {t("dashboard.addPlant")}
          </button>
        </div>
        <Link to="/" className="text-link">
          {t("plants.goDashboard")}
        </Link>
        {addPlantModal}
        {deletePlantModal}
        {renamePlantModal}
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">{t("plants.title")}</h1>
          <p className="muted page-lead">{t("plants.subtitle")}</p>
        </div>
        <button type="button" className="btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={18} />
          {t("dashboard.addPlant")}
        </button>
      </div>
      <div className="plants-grid">
        {plants.map((plant) => {
          const condition = conditionByPlant[plant.id];
          const health = condition?.health_score ?? plant.health;
          const conditionLabel = condition?.condition_status
            ? label("condition", condition.condition_status)
            : t("common.loading");

          return (
            <article key={plant.id} className="plant-tile card">
              <Link
                to={`/plants/${plant.id}`}
                state={{ backTo: "/plants", backLabelKey: "common.backToPlants" }}
                className="plant-tile-link"
              >
                <div className="plant-tile-img">
                  {plant.image_url ? <img src={plant.image_url} alt={plant.name} /> : <span>{plant.name.charAt(0)}</span>}
                </div>
                <div className="plant-tile-body">
                  <div>
                    <h3>{plant.name}</h3>
                    <p className="muted">{displayPlantSpecies(plant.species, t)}</p>
                  </div>
                  <div className="plant-tile-info">
                    <span>
                      <MapPin size={16} />
                      {plant.location ?? t("plants.locationNotSet")}
                    </span>
                    <span>
                      <Hash size={16} />
                      {plant.id}
                    </span>
                    <span>
                      <Activity size={16} />
                      {conditionLabel}
                    </span>
                    <span>
                      <Activity size={16} />
                      {health != null ? `${health}%` : t("common.loading")}
                    </span>
                  </div>
                  {plant.description?.trim() ? <p className="muted plant-tile-note">{plant.description}</p> : null}
                  <span className="text-link">{t("dashboard.viewDetails")}</span>
                </div>
              </Link>
              <button
                type="button"
                className="plant-delete-btn"
                title={t("plants.delete")}
                aria-label={t("plants.delete")}
                onClick={() => setPlantToDelete({ id: plant.id, name: plant.name })}
              >
                <Trash2 size={18} />
              </button>
              <button
                type="button"
                className="plant-edit-btn"
                title={t("plants.rename")}
                aria-label={t("plants.rename")}
                onClick={() => openRenameDialog({ id: plant.id, name: plant.name })}
              >
                <Pencil size={18} />
              </button>
            </article>
          );
        })}
      </div>
      {addPlantModal}
      {deletePlantModal}
      {renamePlantModal}
    </div>
  );
}
