import { useState } from 'react';
import { SplitPane } from '../components/layout/SplitPane';
import { InteractionForm } from '../features/interactions/InteractionForm';
import { ChatPlaceholder } from '../features/chat/ChatPlaceholder';
import { ConfirmModal } from '../components/ui/confirmModal';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { logout } from '../features/auth/authSlice';
import { Button } from '../components/ui/button';
import { LogOut, User as UserIcon } from 'lucide-react';

export function Dashboard() {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { dirty } = useAppSelector((state) => state.interactions);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = () => {
    if (dirty) {
      setShowLogoutConfirm(true);
    } else {
      dispatch(logout());
    }
  };

  return (
    <div className="flex h-screen flex-col">
      <header className="flex h-14 items-center justify-between border-b bg-background px-6">
        <h1 className="text-lg font-semibold">HCP Agent</h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <UserIcon className="h-4 w-4" />
            <span>{user?.name}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sign Out
          </Button>
        </div>
      </header>
      <div className="flex-1 overflow-hidden">
        <SplitPane
          left={<InteractionForm />}
          right={<ChatPlaceholder />}
          initialPosition={65}
        />
      </div>
      <ConfirmModal
        isOpen={showLogoutConfirm}
        title="Unsaved Changes"
        message="You have unsaved changes. Are you sure you want to sign out? Your changes will be lost."
        confirmText="Sign Out"
        cancelText="Cancel"
        onConfirm={() => {
          setShowLogoutConfirm(false);
          dispatch(logout());
        }}
        onCancel={() => setShowLogoutConfirm(false)}
        variant="destructive"
      />
    </div>
  );
}
