import { useState, useEffect, useRef } from 'react';
import {
  Search,
  Plus,
  X,
  Mic,
  Sparkles,
  Check,
  Trash2,
  Users,
  FileText,
  Package,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Minus,
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Select } from '../../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { ConfirmModal } from '../../components/ui/confirmModal';
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { useClickOutside } from '../../hooks/useClickOutside';
import {
  updateFormField,
  setHCP,
  setSentiment,
  addAttendee,
  removeAttendee,
  addMaterial,
  removeMaterial,
  addSample,
  removeSample,
  resetForm,
  clearDirty,
  createInteraction,
} from './interactionsSlice';
import { searchHCPs, fetchHCPs } from '../hcps/hcpsSlice';
import { fetchMaterials } from '../materials/materialsSlice';
import { searchSamples, fetchSamples } from '../samples/samplesSlice';
import type { HCP, Material, Sample, Sentiment, InteractionType } from '../../types';

const INTERACTION_TYPES: { value: InteractionType; label: string }[] = [
  { value: 'meeting', label: 'Meeting' },
  { value: 'call', label: 'Phone Call' },
  { value: 'conference', label: 'Conference' },
  { value: 'email', label: 'Email' },
];

const SENTIMENTS: { value: Sentiment; label: string; icon: React.ReactNode; color: string }[] = [
  { value: 'positive', label: 'Positive', icon: <ThumbsUp className="h-5 w-5" />, color: 'text-green-500' },
  { value: 'neutral', label: 'Neutral', icon: <Minus className="h-5 w-5" />, color: 'text-yellow-500' },
  { value: 'negative', label: 'Negative', icon: <ThumbsDown className="h-5 w-5" />, color: 'text-red-500' },
];

export function InteractionForm() {
  const dispatch = useAppDispatch();
  const { formData, dirty } = useAppSelector((state) => state.interactions);
  const { searchResults } = useAppSelector((state) => state.hcps);
  const { items: materials } = useAppSelector((state) => state.materials);
  const { suggestions } = useAppSelector((state) => state.followUps);
  const { user } = useAppSelector((state) => state.auth);
  const { searchResults: sampleSearchResults } = useAppSelector((state) => state.samples);

  const [hcpSearchOpen, setHcpSearchOpen] = useState(false);
  const [hcpSearchQuery, setHcpSearchQuery] = useState('');
  const [materialSearchOpen, setMaterialSearchOpen] = useState(false);
  const [sampleSearchOpen, setSampleSearchOpen] = useState(false);
  const [sampleSearchQuery, setSampleSearchQuery] = useState('');
  const [selectedSample, setSelectedSample] = useState<Sample | null>(null);
  const [newAttendee, setNewAttendee] = useState('');
  const [sampleQty, setSampleQty] = useState(1);
  const [saving, setSaving] = useState(false);

  const hcpRef = useRef<HTMLDivElement>(null);
  const materialRef = useRef<HTMLDivElement>(null);
  const sampleRef = useRef<HTMLDivElement>(null);
  const [showNewInteractionConfirm, setShowNewInteractionConfirm] = useState(false);

  useClickOutside(hcpRef, () => setHcpSearchOpen(false), hcpSearchOpen);
  useClickOutside(materialRef, () => setMaterialSearchOpen(false), materialSearchOpen);
  useClickOutside(sampleRef, () => setSampleSearchOpen(false), sampleSearchOpen);

  useEffect(() => {
    dispatch(fetchHCPs());
    dispatch(fetchMaterials());
    dispatch(fetchSamples(undefined));
  }, [dispatch]);

  const handleNewInteraction = () => {
    if (dirty) {
      setShowNewInteractionConfirm(true);
    } else {
      dispatch(resetForm());
      setHcpSearchQuery('');
    }
  };

  const confirmNewInteraction = () => {
    setShowNewInteractionConfirm(false);
    dispatch(resetForm());
    setHcpSearchQuery('');
  };

  const handleSampleSearch = (query: string) => {
    setSampleSearchQuery(query);
    dispatch(searchSamples(query));
    setSampleSearchOpen(true);
  };

  const handleAddSample = (sample: Sample) => {
    const newSample: Sample = {
      id: Math.random().toString(36).substring(2, 9),
      productName: sample.productName,
      lotNumber: sample.lotNumber,
      quantity: sampleQty,
      createdAt: new Date().toISOString(),
    };
    dispatch(addSample(newSample));
    setSelectedSample(null);
    setSampleSearchQuery('');
    setSampleQty(1);
    setSampleSearchOpen(false);
  };

  const handleAddSampleFromSearch = () => {
    if (selectedSample) {
      handleAddSample(selectedSample);
    }
  };

  const handleHcpSearch = (query: string) => {
    setHcpSearchQuery(query);
    if (query.length >= 2) {
      dispatch(searchHCPs(query));
      setHcpSearchOpen(true);
    }
  };

  const selectHCP = (hcp: HCP) => {
    dispatch(setHCP(hcp));
    setHcpSearchOpen(false);
    setHcpSearchQuery(hcp.name);
  };

  const clearHCP = () => {
    dispatch(updateFormField({ field: 'hcpId', value: undefined }));
    dispatch(updateFormField({ field: 'hcp', value: undefined }));
    setHcpSearchQuery('');
  };

  const handleAddAttendee = () => {
    if (newAttendee.trim()) {
      dispatch(addAttendee(newAttendee.trim()));
      setNewAttendee('');
    }
  };

  const handleAddMaterial = (material: Material) => {
    dispatch(addMaterial(material));
    setMaterialSearchOpen(false);
  };

  const handleSave = async () => {
    if (!formData.hcpId || !formData.dateTime) return;
    
    setSaving(true);
    try {
      const interactionData = {
        hcpId: formData.hcpId,
        type: formData.type || 'meeting',
        dateTime: formData.dateTime,
        topics: formData.topics,
        sentiment: formData.sentiment,
        outcome: formData.outcome,
        attendees: formData.attendees || [],
        materials: formData.materials,
        samples: formData.samples,
      };
      
      await dispatch(createInteraction(interactionData)).unwrap();
      dispatch(clearDirty());
    } catch (error) {
      console.error('Failed to save interaction:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={handleNewInteraction}>
            <Plus className="mr-2 h-4 w-4" />
            New Interaction
          </Button>
          {dirty && (
            <Badge variant="destructive">Unsaved changes</Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={!dirty}>
            Cancel
          </Button>
          <Button size="sm" onClick={handleSave} disabled={!formData.hcpId || saving}>
            {saving ? 'Saving...' : (
              <>
                <Check className="mr-2 h-4 w-4" />
                Save
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="space-y-6">
          {/* Basic Details */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Users className="h-5 w-5" />
                Basic Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">HCP Name *</label>
                <div className="relative" ref={hcpRef}>
                  <Input
                    placeholder="Search HCP..."
                    value={formData.hcp ? formData.hcp.name : hcpSearchQuery}
                    onChange={(e) => handleHcpSearch(e.target.value)}
                    onFocus={() => hcpSearchQuery.length >= 2 && setHcpSearchOpen(true)}
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-1">
                    {formData.hcp && (
                      <button
                        type="button"
                        onClick={clearHCP}
                        className="text-muted-foreground hover:text-foreground"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                    <Search className="h-4 w-4 text-muted-foreground" />
                  </div>
                  {hcpSearchOpen && searchResults.length > 0 && (
                    <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-background py-1 shadow-lg">
                      {searchResults.map((hcp) => (
                        <button
                          key={hcp.id}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                          onClick={() => selectHCP(hcp)}
                        >
                          <div className="font-medium">{hcp.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {hcp.specialty} • {hcp.institution}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Interaction Type</label>
                  <Select
                    options={INTERACTION_TYPES}
                    value={formData.type || 'meeting'}
                    onChange={(e) => dispatch(updateFormField({ field: 'type', value: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Date</label>
                  <Input
                    type="date"
                    value={formData.dateTime?.split('T')[0] || ''}
                    onChange={(e) => dispatch(updateFormField({ field: 'dateTime', value: e.target.value }))}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Time</label>
                  <Input
                    type="time"
                    value={formData.dateTime?.split('T')[1]?.slice(0, 5) || ''}
                    onChange={(e) => {
                      const date = formData.dateTime?.split('T')[0] || new Date().toISOString().split('T')[0];
                      dispatch(updateFormField({ field: 'dateTime', value: `${date}T${e.target.value}` }));
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Created By</label>
                  <Input value={user?.name || ''} disabled />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Attendees</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add attendee"
                    value={newAttendee}
                    onChange={(e) => setNewAttendee(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddAttendee()}
                  />
                  <Button variant="outline" onClick={handleAddAttendee}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                {formData.attendees && formData.attendees.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.attendees.map((attendee, index) => (
                      <Badge key={index} variant="secondary" className="gap-1 pr-1">
                        {attendee}
                        <button
                          onClick={() => dispatch(removeAttendee(index))}
                          className="ml-1 rounded-full p-0.5 hover:bg-accent"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Discussion & Notes */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="h-5 w-5" />
                Discussion & Notes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Topics Discussed</label>
                <Textarea
                  placeholder="Enter topics discussed..."
                  rows={4}
                  value={formData.topics || ''}
                  onChange={(e) => dispatch(updateFormField({ field: 'topics', value: e.target.value }))}
                />
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Mic className="mr-2 h-4 w-4" />
                  Dictate
                </Button>
                <Button variant="outline" size="sm">
                  <Sparkles className="mr-2 h-4 w-4" />
                  Summarize from Voice Note
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Materials & Samples */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Package className="h-5 w-5" />
                Materials & Samples
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Materials Shared</label>
                <div className="relative" ref={materialRef}>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setMaterialSearchOpen(!materialSearchOpen)}
                  >
                    <Search className="mr-2 h-4 w-4" />
                    Search/Add Material
                  </Button>
                  {materialSearchOpen && (
                    <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-background py-1 shadow-lg">
                      {materials.map((material) => (
                        <button
                          key={material.id}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                          onClick={() => handleAddMaterial(material)}
                        >
                          <div className="font-medium">{material.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {material.type} • {material.description}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {formData.materials && formData.materials.length > 0 ? (
                  <div className="space-y-2">
                    {formData.materials.map((material) => (
                      <div
                        key={material.id}
                        className="flex items-center justify-between rounded-md border p-2"
                      >
                        <span className="text-sm">{material.name}</span>
                        <button
                          onClick={() => dispatch(removeMaterial(material.id))}
                          className="text-muted-foreground hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No materials added</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Samples Distributed</label>
                <div className="relative" ref={sampleRef}>
                  <Input
                    placeholder="Search sample..."
                    value={selectedSample ? selectedSample.productName : sampleSearchQuery}
                    onChange={(e) => {
                      setSelectedSample(null);
                      handleSampleSearch(e.target.value);
                    }}
                    onFocus={() => sampleSearchQuery && setSampleSearchOpen(true)}
                  />
                  {sampleSearchOpen && sampleSearchResults.length > 0 && (
                    <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-background py-1 shadow-lg">
                      {sampleSearchResults.map((sample) => (
                        <button
                          key={sample.id}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                          onClick={() => {
                            setSelectedSample(sample);
                            setSampleSearchQuery(sample.productName);
                            setSampleSearchOpen(false);
                          }}
                        >
                          <div className="font-medium">{sample.productName}</div>
                          <div className="text-xs text-muted-foreground">
                            Lot: {sample.lotNumber || 'N/A'}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {selectedSample && (
                  <div className="flex items-center gap-2">
                    <div className="flex-1 text-sm text-muted-foreground">
                      {selectedSample.productName}
                      {selectedSample.lotNumber && ` • Lot: ${selectedSample.lotNumber}`}
                    </div>
                    <Input
                      type="number"
                      placeholder="Qty"
                      className="w-24"
                      value={sampleQty}
                      onChange={(e) => setSampleQty(parseInt(e.target.value) || 1)}
                      min={1}
                    />
                    <Button size="sm" onClick={handleAddSampleFromSearch}>
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                )}
                {formData.samples && formData.samples.length > 0 ? (
                  <div className="space-y-2">
                    {formData.samples.map((sample) => (
                      <div
                        key={sample.id}
                        className="flex items-center justify-between rounded-md border p-2"
                      >
                        <span className="text-sm">
                          {sample.productName} (Qty: {sample.quantity})
                          {sample.lotNumber && ` • Lot: ${sample.lotNumber}`}
                        </span>
                        <button
                          onClick={() => dispatch(removeSample(sample.id))}
                          className="text-muted-foreground hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No samples added</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Sentiment & Outcomes */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <ThumbsUp className="h-5 w-5" />
                Sentiment & Outcomes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Observed/Inferred HCP Sentiment</label>
                <div className="flex gap-4">
                  {SENTIMENTS.map((sentiment) => (
                    <button
                      key={sentiment.value}
                      className={`flex items-center gap-2 rounded-md border px-4 py-2 transition-colors ${
                        formData.sentiment === sentiment.value
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:bg-accent'
                      }`}
                      onClick={() => dispatch(setSentiment(sentiment.value))}
                    >
                      <span className={sentiment.color}>{sentiment.icon}</span>
                      <span className="text-sm">{sentiment.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Outcomes</label>
                <Textarea
                  placeholder="Key agreements or results of the meeting..."
                  rows={3}
                  value={formData.outcome || ''}
                  onChange={(e) => dispatch(updateFormField({ field: 'outcome', value: e.target.value }))}
                />
              </div>
            </CardContent>
          </Card>

          {/* Follow-ups */}
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-lg">
                <MessageSquare className="h-5 w-5" />
                Follow-ups
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Manual Follow-up Actions</label>
                <Textarea
                  placeholder="Enter next steps..."
                  rows={2}
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-primary">
                  <Sparkles className="h-4 w-4" />
                  AI Suggested Follow-ups
                </div>
                {suggestions.length > 0 ? (
                  <div className="space-y-2">
                    {suggestions.map((suggestion) => (
                      <div
                        key={suggestion.id}
                        className="flex items-center justify-between rounded-md border border-dashed border-primary/50 bg-primary/5 p-3"
                      >
                        <span className="text-sm">{suggestion.description}</span>
                        <div className="flex gap-2">
                          <Button size="sm" variant="ghost">
                            <Check className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="ghost">
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    AI suggestions will appear here based on interaction context
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <ConfirmModal
        isOpen={showNewInteractionConfirm}
        title="Unsaved Changes"
        message="You have unsaved changes. Are you sure you want to start a new interaction? Your changes will be lost."
        confirmText="Start New"
        cancelText="Cancel"
        onConfirm={confirmNewInteraction}
        onCancel={() => setShowNewInteractionConfirm(false)}
        variant="destructive"
      />
    </div>
  );
}
