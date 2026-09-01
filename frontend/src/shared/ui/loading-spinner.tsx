export function LoadingSpinner({ 'data-testid': dataTestid } : { 'data-testid'?: string } = {}) {
  return (
    <div className="flex justify-center items-center" data-testid={dataTestid || 'loading-spinner'}>
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal"></div>
    </div>
  );
}