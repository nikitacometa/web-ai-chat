import { notFound } from 'next/navigation';

interface PageProps {
  params: { id: string };
}

export default async function WithAppPage({ params }: PageProps) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.aisatisfy.me';

  try {
    const res = await fetch(`${apiUrl}/files/${params.id}.html`, {
      cache: 'no-store', // Always fetch fresh content
    });

    if (!res.ok) {
      return notFound();
    }

    const html = await res.text();

    return (
      <div className="min-h-screen">
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    );
  } catch (error) {
    console.error('Error fetching app HTML:', error);
    return notFound();
  }
}

// Generate metadata for the page
export async function generateMetadata({ params }: PageProps) {
  return {
    title: `App ${params.id} - AI Satisfy`,
    description: `View AI-powered application ${params.id}`,
  };
}
