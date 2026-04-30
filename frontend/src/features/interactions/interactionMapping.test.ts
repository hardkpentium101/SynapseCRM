import { describe, it, expect, vi, beforeEach } from 'vitest';
import interactionsReducer, {
  setFormData,
  resetForm,
} from './interactionsSlice';
import type { Interaction } from '../../types';

const initialFormData: Partial<Interaction> = {
  type: 'meeting',
  dateTime: new Date().toISOString().slice(0, 16),
  attendees: [],
  topics: '',
  sentiment: undefined,
  outcome: '',
};

const mockInteractionFromAI = {
  interaction: {
    hcp_id: '80acd5ad-7a79-4f78-8aed-f558b7a241da',
    type: 'meeting',
    date_time: 'today',
    topics: ['OncoBoost efficacy'],
    sentiment: '',
    outcome: '',
    attendees: [],
    notes: '',
    status: 'need_integration',
    message: 'Create meeting interaction with HCP: 80acd5ad-7a79-4f78-8aed-f558b7a241da',
    hcp_name: 'Dr. Priya Sharma',
    hcp_specialty: 'Oncology',
    hcp_institution: 'Tata Memorial Hospital, Mumbai',
  },
};

describe('Interaction Data Mapping from AI Response', () => {
  const initialState = {
    items: [],
    activeId: null,
    activeInteraction: null,
    formData: initialFormData,
    dirty: false,
    loading: false,
    saving: false,
    error: null,
  };

  const mockInteractionResponse = {
    interaction: {
      hcp_id: '80acd5ad-7a79-4f78-8aed-f558b7a241da',
      type: 'meeting',
      date_time: 'today',
      topics: ['OncoBoost efficacy'],
      sentiment: '',
      outcome: '',
      attendees: [],
      notes: '',
      hcp_name: 'Dr. Priya Sharma',
      hcp_specialty: 'Oncology',
      hcp_institution: 'Tata Memorial Hospital, Mumbai',
    },
  };

  describe('hcp field', () => {
    it('should set hcp object from response with name, specialty, institution', () => {
      const hcpObj = {
        id: mockInteractionFromAI.interaction.hcp_id,
        name: mockInteractionFromAI.interaction.hcp_name || '',
        specialty: mockInteractionFromAI.interaction.hcp_specialty || '',
        institution: mockInteractionFromAI.interaction.hcp_institution || '',
      };
      const state = interactionsReducer(
        initialState,
        setFormData({ hcp: hcpObj })
      );
      expect(state.formData.hcp).toEqual({
        id: '80acd5ad-7a79-4f78-8aed-f558b7a241da',
        name: 'Dr. Priya Sharma',
        specialty: 'Oncology',
        institution: 'Tata Memorial Hospital, Mumbai',
      });
    });

    it('should have hcp name from response', () => {
      expect(mockInteractionFromAI.interaction.hcp_name).toBe('Dr. Priya Sharma');
    });

    it('should have hcp specialty from response', () => {
      expect(mockInteractionFromAI.interaction.hcp_specialty).toBe('Oncology');
    });

    it('should have hcp institution from response', () => {
      expect(mockInteractionFromAI.interaction.hcp_institution).toBe('Tata Memorial Hospital, Mumbai');
    });
  });

  describe('type field', () => {
    it('should set type from response', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ type: mockInteractionFromAI.interaction.type as 'meeting' })
      );
      expect(state.formData.type).toBe('meeting');
    });
  });

  describe('date_time field', () => {
    it('should set date_time from response', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ dateTime: mockInteractionFromAI.interaction.date_time })
      );
      expect(state.formData.dateTime).toBe('today');
    });

    it('should fall back to current timestamp if date_time is missing', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ dateTime: new Date().toISOString().slice(0, 16) })
      );
      expect(state.formData.dateTime).toBeDefined();
    });
  });

  describe('topics field', () => {
    it('should convert topics array to comma-separated string', () => {
      const topicsString = mockInteractionFromAI.interaction.topics.join(', ');
      const state = interactionsReducer(
        initialState,
        setFormData({ topics: topicsString })
      );
      expect(state.formData.topics).toBe('OncoBoost efficacy');
    });

    it('should handle multiple topics', () => {
      const multipleTopics = ['OncoBoost efficacy', 'Clinical trials', 'New drugs'];
      const topicsString = multipleTopics.join(', ');
      const state = interactionsReducer(
        initialState,
        setFormData({ topics: topicsString })
      );
      expect(state.formData.topics).toBe('OncoBoost efficacy, Clinical trials, New drugs');
    });
  });

  describe('attendees field', () => {
    it('should set attendees array from response', () => {
      const attendees = ['Dr. Smith', 'Dr. Jones'];
      const state = interactionsReducer(
        initialState,
        setFormData({ attendees: attendees })
      );
      expect(state.formData.attendees).toEqual(['Dr. Smith', 'Dr. Jones']);
    });

    it('should handle empty attendees array', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ attendees: [] })
      );
      expect(state.formData.attendees).toEqual([]);
    });
  });

  describe('sentiment field', () => {
    it('should set sentiment when provided', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ sentiment: 'positive' as 'positive' })
      );
      expect(state.formData.sentiment).toBe('positive');
    });
  });

  describe('outcome field', () => {
    it('should set outcome from response', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ outcome: 'Follow-up scheduled' })
      );
      expect(state.formData.outcome).toBe('Follow-up scheduled');
    });
  });

  describe('notes field', () => {
    it('should set notes from response', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ notes: 'Discussion went well' })
      );
      expect(state.formData.notes).toBe('Discussion went well');
    });
  });

  describe('Full interaction data mapping', () => {
    it('should map all fields correctly from AI response', () => {
      const interaction = mockInteractionFromAI.interaction;
      
      const state = interactionsReducer(
        initialState,
        setFormData({
          hcpId: interaction.hcp_id,
          type: interaction.type as 'meeting',
          dateTime: interaction.date_time,
          topics: interaction.topics?.join(', '),
          attendees: interaction.attendees,
          sentiment: (interaction.sentiment || 'neutral') as 'positive',
          outcome: interaction.outcome,
          notes: interaction.notes,
        })
      );

      expect(state.formData.hcpId).toBe('80acd5ad-7a79-4f78-8aed-f558b7a241da');
      expect(state.formData.type).toBe('meeting');
      expect(state.formData.dateTime).toBe('today');
      expect(state.formData.topics).toBe('OncoBoost efficacy');
      expect(state.formData.attendees).toEqual([]);
      expect(state.formData.sentiment).toBe('neutral');
      expect(state.formData.outcome).toBe('');
      expect(state.formData.notes).toBe('');
    });

    it('should set dirty flag when form data is updated', () => {
      const state = interactionsReducer(
        initialState,
        setFormData({ hcpId: 'some-id' })
      );
      expect(state.dirty).toBe(true);
    });

    it('should have all 14 fields from the AI response', () => {
      const interaction = mockInteractionFromAI.interaction;
      
      const allFields = {
        hcpId: interaction.hcp_id,
        type: interaction.type,
        dateTime: interaction.date_time,
        topics: interaction.topics?.join(', '),
        attendees: interaction.attendees,
        sentiment: interaction.sentiment,
        outcome: interaction.outcome,
        notes: interaction.notes,
        status: interaction.status,
        message: interaction.message,
        hcpName: interaction.hcp_name,
        hcpSpecialty: interaction.hcp_specialty,
        hcpInstitution: interaction.hcp_institution,
      };

      expect(Object.keys(allFields).length).toBe(13);
      expect(allFields.hcpId).toBe('80acd5ad-7a79-4f78-8aed-f558b7a241da');
      expect(allFields.type).toBe('meeting');
      expect(allFields.dateTime).toBe('today');
      expect(allFields.topics).toBe('OncoBoost efficacy');
      expect(allFields.attendees).toEqual([]);
      expect(allFields.sentiment).toBe('');
      expect(allFields.outcome).toBe('');
      expect(allFields.notes).toBe('');
      expect(allFields.status).toBe('need_integration');
      expect(allFields.message).toBe('Create meeting interaction with HCP: 80acd5ad-7a79-4f78-8aed-f558b7a241da');
      expect(allFields.hcpName).toBe('Dr. Priya Sharma');
      expect(allFields.hcpSpecialty).toBe('Oncology');
      expect(allFields.hcpInstitution).toBe('Tata Memorial Hospital, Mumbai');
    });
  });

  describe('Reset form', () => {
    it('should reset form data to initial state', () => {
      const stateWithData = interactionsReducer(
        initialState,
        setFormData({ hcpId: 'some-id', type: 'meeting' })
      );
      
      const resetState = interactionsReducer(stateWithData, resetForm());
      
      expect(resetState.formData.type).toBe(initialFormData.type);
      expect(resetState.dirty).toBe(false);
      expect(resetState.activeId).toBeNull();
    });
  });
});